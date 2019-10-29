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
import nanaimo.pytest_plugin


class Fixture(nanaimo.Fixture):
    """
    Gathers a log over a serial connection until a given pattern is matched.
    """

    fixture_name = 'serial_log_watch'
    argument_prefix = 'lw'

    def __init__(self,
                 manager: nanaimo.FixtureManager,
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

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Watch the logs until the pattern matches.
        """
        with self._uart_factory(args.lw_port, args.lw_port_speed) as monitor:
            disturb_rate = args.lw_disturb_rate
            if disturb_rate is not None and float(disturb_rate) > 0:
                while True:
                    done, pending = await asyncio.wait([asyncio.ensure_future(self._matcher(args, monitor)),
                                                        asyncio.ensure_future(self._agitator(args, monitor))])
                    if len(done) == 2:
                        done0 = done.pop().result()
                        done1 = done.pop().result()
                        artifacts = nanaimo.Artifacts.combine(done0, done1)
                        break
            else:
                artifacts = await self._matcher(args, monitor)

        self._logger.info('Found match : %s', artifacts.matched_line)
        return artifacts

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+

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
        artifacts = nanaimo.Artifacts()
        await asyncio.sleep(args.lw_disturb_rate)
        self._logger.debug('About to disturb the uart...')
        await monitor.put_line(args.lw_disruption)
        return artifacts


@nanaimo.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Fixture


@pytest.fixture
def serial_log_watch(request: typing.Any) -> nanaimo.Fixture:
    return nanaimo.pytest_plugin.create_pytest_fixture(request, Fixture)
