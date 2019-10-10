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
import contextlib
import pathlib
import re
import typing

import nanaimo
from nanaimo.connections.uart import AbstractAsyncSerial, ConcurrentUart


class Series1900BUart(nanaimo.Fixture):
    """
    Control of a 1900B series BK Precision power supply via UART.
    """

    fixture_name = 'bkprecision'

    DefaultCommandTimeoutSeconds = 6.0

    # cspell: disable
    CommandTurnOn = 'SOUT0'
    CommandTurnOff = 'SOUT1'
    CommandGetDisplay = 'GETD'

    ResultOk = 'OK'

    StatusCV = 0
    StatusCC = 1

    CommandHelp = {
        'SOUT0': 'Switch on supply output.',
        'SOUT1': 'Switch off supply output.',
        'GETD': 'Read parameters displayed on the front panel of the supply.'
    }

    # cspell: enable

    _debug = False

    UartFactoryType = typing.Callable[[typing.Union[str, pathlib.Path]], typing.Any]
    """
    The serial port factory type for this instrument.
    """

    @classmethod
    @contextlib.contextmanager
    def default_serial_port(cls, port: typing.Union[str, pathlib.Path]) -> typing.Generator[AbstractAsyncSerial, None, None]:
        """
        Creates a serial connection to the given port using the default settings for a BK Precision Series 1900B
        power supply.
        """
        with ConcurrentUart.new_default(str(port), 9600) as bk_uart:
            bk_uart.eol = '\r'
            yield bk_uart

    def __init__(self,
                 manager: 'nanaimo.FixtureManager',
                 loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                 uart_factory: typing.Optional[UartFactoryType] = None):
        super().__init__(manager, loop)
        self._uart_factory = (uart_factory if uart_factory is not None else self.default_serial_port)

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--bk-port',
                               help='The port the BK Precision power supply is connected to.')
        arguments.add_argument('--bk-command', '--BC',
                               help='command', default='?')
        arguments.add_argument('--bk-command-timeout',
                               help='time out for individual commands.', default=4.0)
        arguments.add_argument('--bk-target-voltage',
                               help='The target voltage')

    async def gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Send a command to the instrument and return the result.
        :param str command: Send one of the following commands:

            +---------+----------------------------------+--------------------------------------------------+
            | Command | Action                           | Returns                                          |
            +=========+==================================+==================================================+
            | '1'     | Turn on output voltage           | 'OK' or error text.                              |
            +---------+----------------------------------+--------------------------------------------------+
            | '2''    | Turn off output voltage          | 'OK' or error text                               |
            +---------+----------------------------------+--------------------------------------------------+
            | 'r'     | Send a stream of <cr> characters | (NA)                                             |
            +---------+----------------------------------+--------------------------------------------------+
            | '?'     | Read the front panel display     | Display voltage, current, and status (ON or OFF) |
            +---------+----------------------------------+--------------------------------------------------+
        """

        artifacts = nanaimo.Artifacts(-1)

        with self._uart_factory(str(args.bk_port)) as bk_uart:
            if args.bk_command == '1':
                _, artifacts.result_code = await self._do_command(bk_uart, self.CommandTurnOn, args.bk_command_timeout)
                if artifacts.result_code == 0 and args.bk_target_voltage is not None:
                    artifacts.result_code = await self._wait_for_voltage(bk_uart, args.bk_command_timeout, True, float(args.bk_target_voltage) - .2)
            elif args.bk_command == '0':
                _, artifacts.result_code = await self._do_command(bk_uart, self.CommandTurnOff, args.bk_command_timeout)
                if artifacts.result_code == 0 and args.bk_target_voltage is not None:
                    artifacts.result_code = await self._wait_for_voltage(bk_uart, args.bk_command_timeout, False, 1)
            elif args.bk_command == 'r':
                _, artifacts.result_code = await self._do_command(bk_uart, '\r\r\r\r', args.bk_command_timeout)
            elif args.bk_command == '?':
                display, artifacts.result_code = await self._get_display(bk_uart, args.bk_command_timeout)
                if artifacts.result_code == 0:
                    setattr(artifacts, 'display', display)
                    setattr(artifacts, 'display_text', '{},{},{}'.format(display[0], display[1], ('CV' if display[2] == self.StatusCV else 'CC')))
            else:
                self.logger.warn('command {} is not a valid Series1900BUart command.'.format(args.bk_command))

        return artifacts

    async def _get_display(self, uart: AbstractAsyncSerial, command_timeout: float) -> typing.Tuple[typing.Tuple[float, float, int], int]:
        display, status = await self._do_command(uart, self.CommandGetDisplay, command_timeout)
        if display is None or len(display) < 8:
            return ((0, 0, 0), -1)
        else:
            voltage = int(display[0:4]) / 100.0
            current = int(display[4:8]) / 100.0
            status = int(display[8])
            return ((voltage, current, status), 0)

    async def _do_command(self, uart: AbstractAsyncSerial, command: str, command_timeout: float) -> typing.Tuple[str, int]:
        try:
            command_help = self.CommandHelp[command]
            is_command = True
            self.logger.debug('Sending command %s (help=%s)', command, command_help)
        except KeyError:
            self.logger.debug('Sending characters %s', re.sub('\\r', '<cr>', command))
            is_command = False

        puttime_secs = await uart.put_line(command + '\r')
        previous_line = None
        status = 1
        if is_command:
            start_time = uart.time()
            while True:
                now = uart.time()
                if command_timeout > 0 and now - start_time > command_timeout:
                    raise asyncio.TimeoutError()
                if self._debug:
                    self.logger.debug('Waiting for response to command %s put before time %f seconds', command, puttime_secs)
                received_line = await uart.get_line((command_timeout - (now - start_time) if command_timeout > 0 else 0))
                if self._debug:
                    self.logger.debug('At %f Got line: %s', received_line.timestamp_seconds, received_line)
                # The result has to be from after the put or
                # it's an old result from a buffer.
                if received_line.timestamp_seconds > puttime_secs and received_line == self.ResultOk:
                    status = 0
                    break
                # Skip any empty lines the device sends back.
                if len(received_line) > 0:
                    previous_line = received_line
        return (str(previous_line), status)

    async def _wait_for_voltage(self, uart: AbstractAsyncSerial, command_timeout: float, is_min: bool, threshold_v: float) -> int:
        while True:
            # TODO: timeout
            display_tuple, result = await self._get_display(uart, command_timeout)
            voltage = display_tuple[0]
            if (voltage >= threshold_v if is_min else voltage <= threshold_v):
                if is_min:
                    self.logger.debug('---------------POWER SUPPLY UP----------------')
                else:
                    self.logger.debug('--------------POWER SUPPLY DOWN---------------')
                break
            await asyncio.sleep(.1)
        return result


@nanaimo.FixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Series1900BUart
