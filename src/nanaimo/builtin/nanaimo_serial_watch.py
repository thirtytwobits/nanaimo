#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
#                                       (@@@@%%%%%%%%%&@@&.
#                              /%&&%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%&@@(
#                              *@&%%%%%%%%%&&%%%%%%%%%%%%%%%%%%&&&%%%%%%%
#                               @   @@@(@@@@%%%%%%%%%%%%%%%%&@@&* @@@   .
#                               ,   .        .  .@@@&                   /
#                                .       .                              *
#                               @@              .                       @
#                              @&&&&&&@. .    .                     *@%&@
#                              &&&&&&&&&&&&&&&&@@        *@@############@
#                     *&/ @@ #&&&&&&&&&&&&&&&&&&&&@  ###################*
#                              @&&&&&&&&&&&&&&&&&&##################@
#                                 %@&&&&&&&&&&&&&&################@
#                                        @&&&&&&&&&&%#######&@%
#  nanaimo                                   (@&&&&####@@*
#
import asyncio
import re
import typing

import pytest

import nanaimo
import nanaimo.connections
import nanaimo.connections.uart
import nanaimo.fixtures
import nanaimo.pytest.plugin


class Fixture(nanaimo.fixtures.Fixture):
    """
    Gathers a log over a serial connection until a given pattern is matched.
    """

    fixture_name = 'nanaimo_serial_watch'
    argument_prefix = 'lw'

    def __init__(self,
                 manager: nanaimo.fixtures.FixtureManager,
                 args: nanaimo.Namespace,
                 **kwargs: typing.Any) -> None:
        super().__init__(manager, args, **kwargs)
        if 'uart_factory' in kwargs:
            self._uart_factory = typing.cast(typing.Callable[[str, int], nanaimo.connections.uart.ConcurrentUart],
                                             kwargs['uart_factory'])
        else:
            self._uart_factory = nanaimo.connections.uart.ConcurrentUart.new_default

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        nanaimo.connections.uart.ConcurrentUart.on_visit_test_arguments(arguments)
        arguments.add_argument('--lw-pattern',
                               default='.*',
                               enable_default_from_environ=True,
                               help='A python regular expression to search for')
        arguments.add_argument('--lw-disruption', default='\r\n')
        arguments.add_argument('--lw-disturb-rate', type=float)
        arguments.add_argument('--lw-update-period', type=float, default=1.0, help='Fractional time in seconds')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Watch the logs until the pattern matches.

        +--------------+---------------------------+-----------------------------------------------+
        | **Returned Artifacts**                                                                   |
        +--------------+---------------------------+-----------------------------------------------+
        | key          | type                      | Notes                                         |
        +==============+===========================+===============================================+
        | match        | re.MatchObject            | The match if result_code is 0                 |
        +--------------+---------------------------+-----------------------------------------------+
        | matched_line | str                       | The full line matched if result_code is 0     |
        +--------------+---------------------------+-----------------------------------------------+
        """
        with self._uart_factory(args.lw_port, args.lw_port_speed) as monitor:

            match_future, _ = await self.gate_tasks(self._matcher(args, monitor),
                                                    0.0,
                                                    self._agitator(args, monitor),
                                                    self._updater(args))

        artifacts = typing.cast(nanaimo.Artifacts, match_future.result())
        self._logger.info('Found match : %s', artifacts.matched_line)
        return artifacts

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+
    async def _updater(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        if args.lw_update_period is not None:
            while True:
                await asyncio.sleep(args.lw_update_period)
                self._logger.info('still waiting...')

        return nanaimo.Artifacts()

    async def _matcher(self, args: nanaimo.Namespace,
                       monitor: nanaimo.connections.uart.ConcurrentUart) -> nanaimo.Artifacts:
        artifacts = nanaimo.Artifacts()
        pattern = re.compile(args.lw_pattern)

        self._logger.debug('Starting to look for pattern : %s', str(pattern))
        while True:
            result = await monitor.get_line()
            match = pattern.search(result)
            if match:
                setattr(artifacts, 'match', match)
                setattr(artifacts, 'matched_line', result)
                break

        return artifacts

    async def _agitator(self, args: nanaimo.Namespace,
                        monitor: nanaimo.connections.uart.ConcurrentUart) -> nanaimo.Artifacts:
        if args.lw_disturb_rate is not None:
            while True:
                await asyncio.sleep(args.lw_disturb_rate)
                self._logger.debug('About to disturb the uart...')
                await monitor.put_line(args.lw_disruption)
        return nanaimo.Artifacts()


@nanaimo.fixtures.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_serial_watch(request: typing.Any) -> nanaimo.fixtures.Fixture:
    """
    This Nanaimo fixture allows a test to monitor a serial port until a provided pattern matches.
    The `pytest fixture <https://docs.pytest.org/en/latest/fixture.html>`_ provides
    a :class:`nanaimo.builtin.nanaimo_serial_watch.Fixture` fixture to a pytest.

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :rtype: nanaimo.builtin.nanaimo_serial_watch.Fixture
    """
    return nanaimo.pytest.plugin.create_pytest_fixture(request, Fixture.get_canonical_name())
