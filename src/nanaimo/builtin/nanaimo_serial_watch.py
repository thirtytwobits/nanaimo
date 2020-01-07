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
import textwrap
import typing

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
        arguments.add_argument('--pattern',
                               default='.*',
                               enable_default_from_environ=True,
                               help=textwrap.dedent('''
                A Python regular expression that will be matched against each line of
                serial input received. This fixture gathers input until either this
                pattern is matched or the gather times out.''').lstrip())
        arguments.add_argument('--disruption', default='\r\n', help=textwrap.dedent('''
                Characters to send periodically on the serial link in an attempt to wake
                up connected hosts and get a default response.''').lstrip())
        arguments.add_argument('--disturb-rate', type=float, help=textwrap.dedent('''
                The rate at which the watcher will input the disruption characters to try
                to get the device on the other end of the serial pipe to respond
                (in fractional seconds)''').lstrip())
        arguments.add_argument('--update-period',
                               type=float,
                               help=textwrap.dedent('''
                The rate at which a message is logged when waiting for a log time. This
                provides feedback that the fixture is still active but that the pattern
                has not yet been matched. Omit to squelch the update message.
                (This argument is in fractional seconds).
                            ''').lstrip())

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
        lw_port = self.get_arg_covariant_or_fail(args, 'port')
        lw_port_speed = self.get_arg_covariant_or_fail(args, 'port_speed')

        with self._uart_factory(lw_port, lw_port_speed) as monitor:

            match_future, _ = await self.gate_tasks(self._matcher(args, monitor),
                                                    None,
                                                    self._agitator(args, monitor),
                                                    self._updater(args))

        artifacts = typing.cast(nanaimo.Artifacts, match_future.result())
        self._logger.info('Found match : %s', artifacts.matched_line)
        return artifacts

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+
    async def _updater(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        lw_update_period = self.get_arg_covariant(args, 'update_period')
        if lw_update_period is not None:
            while True:
                await asyncio.sleep(lw_update_period)
                self._logger.info('still waiting...')

        return nanaimo.Artifacts()

    async def _matcher(self, args: nanaimo.Namespace,
                       monitor: nanaimo.connections.uart.ConcurrentUart) -> nanaimo.Artifacts:
        artifacts = nanaimo.Artifacts()
        lw_pattern = self.get_arg_covariant_or_fail(args, 'pattern')
        pattern = re.compile(lw_pattern)

        self._logger.info('Starting to look for pattern : %s', str(lw_pattern))
        while True:
            result = await monitor.get_line()
            result_stripped = result.rstrip()
            if len(result_stripped) > 0:
                self._logger.debug(result_stripped)
            match = pattern.search(result)
            if match:
                setattr(artifacts, 'match', match)
                setattr(artifacts, 'matched_line', result)
                break

        return artifacts

    async def _agitator(self, args: nanaimo.Namespace,
                        monitor: nanaimo.connections.uart.ConcurrentUart) -> nanaimo.Artifacts:
        lw_disturb_rate = self.get_arg_covariant(args, 'disturb_rate')
        lw_disruption = self.get_arg_covariant_or_fail(args, 'disruption')
        if lw_disturb_rate is not None:
            while True:
                await asyncio.sleep(lw_disturb_rate)
                self._logger.debug('About to disturb the uart...')
                await monitor.put_line(lw_disruption)
        return nanaimo.Artifacts()


def pytest_nanaimo_fixture_type() -> typing.Type['Fixture']:
    return Fixture
