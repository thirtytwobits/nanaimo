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
import nanaimo.fixtures
import nanaimo.pytest.plugin
from nanaimo.connections.uart import AbstractAsyncSerial, ConcurrentUart


class Series1900BUart(nanaimo.fixtures.Fixture):
    """
    Control of a 1900B series BK Precision power supply via UART.
    """

    fixture_name = 'nanaimo_instr_bk_precision'
    argument_prefix = 'bk'

    DefaultCommandTimeoutSeconds = 6.0

    # cspell: disable
    CommandTurnOn = 'SOUT0'
    CommandTurnOff = 'SOUT1'
    CommandGetDisplay = 'GETD'

    ResultOk = 'OK'

    ModeCV = 0
    ModeCC = 1
    ModeInvalid = -1

    @classmethod
    def mode_to_text(cls, mode: int) -> str:
        """
        Get a two-character textual representation for a given power supply mode.
        """
        if mode == cls.ModeCV:
            return 'CV'
        elif mode == cls.ModeCC:
            return 'CC'
        else:
            return 'EE'

    CommandHelp = {
        'SOUT0': 'Switch on supply output.',
        'SOUT1': 'Switch off supply output.',
        'GETD': 'Read parameters displayed on the front panel of the supply.'
    }

    # cspell: enable

    UartFactoryType = typing.Callable[[typing.Union[str, pathlib.Path]], typing.Any]
    """
    The serial port factory type for this instrument.
    """

    @classmethod
    @contextlib.contextmanager
    def default_serial_port(cls,
                            port: typing.Union[str, pathlib.Path]) \
            -> typing.Generator[AbstractAsyncSerial, None, None]:
        """
        Creates a serial connection to the given port using the default settings for a BK Precision Series 1900B
        power supply.
        """
        with ConcurrentUart.new_default(str(port), 9600) as bk_uart:
            bk_uart.eol = '\r'
            yield bk_uart

    def __init__(self,
                 manager: nanaimo.fixtures.FixtureManager,
                 args: nanaimo.Namespace,
                 **kwargs: typing.Any):
        super().__init__(manager, args, **kwargs)
        self._debug = False
        if 'uart_factory' in kwargs:
            uart_factory = typing.cast(typing.Optional['Series1900BUart.UartFactoryType'], kwargs['uart_factory'])
            self._uart_factory = (uart_factory if uart_factory is not None else self.default_serial_port)
        else:
            self._uart_factory = self.default_serial_port

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--port',
                               enable_default_from_environ=True,
                               help='The port the BK Precision power supply is connected to.')
        arguments.add_argument('--command', '--BC',
                               help='command', default='?')
        arguments.add_argument('--command-timeout',
                               enable_default_from_environ=True,
                               help='time out for individual commands.', default=4.0)
        arguments.add_argument('--target-voltage',
                               enable_default_from_environ=True,
                               type=float,
                               help='The target voltage')
        arguments.add_argument('--target-voltage-threshold-rising',
                               enable_default_from_environ=True,
                               type=float,
                               default=0.2,
                               help='Voltage offset from the target voltage to trigger on when the voltage is rising.')
        arguments.add_argument('--target-voltage-threshold-falling',
                               enable_default_from_environ=True,
                               type=float,
                               default=0.01,
                               help='Voltage offset from the target voltage to trigger on when the voltage is falling.')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Send a command to the instrument and return the result.
        :param str command: Send one of the following commands:

            +---------+----------------------------------+--------------------------------------------------+
            | Command | Action                           | Returns                                          |
            +=========+==================================+==================================================+
            | '1'     | Turn on output voltage           | 'OK' or error text.                              |
            +---------+----------------------------------+--------------------------------------------------+
            | '0'     | Turn off output voltage          | 'OK' or error text                               |
            +---------+----------------------------------+--------------------------------------------------+
            | 'r'     | Send a stream of <cr> characters | (NA)                                             |
            +---------+----------------------------------+--------------------------------------------------+
            | '?'     | Read the front panel display     | Display voltage, current, and status (ON or OFF) |
            +---------+----------------------------------+--------------------------------------------------+
        """
        bk_port = self.get_arg_covariant_or_fail(args, 'port')
        with self._uart_factory(bk_port) as bk_uart:
            artifacts = await self._do_command_from_args(bk_uart, args)

        return artifacts

    def is_volage_above_on_threshold(self, voltage: float) -> bool:
        """
        Deprecated misspelling. See :meth:`is_voltage_above_on_threshold`
        for correct method.
        """
        return self.is_voltage_above_on_threshold(voltage)

    def is_voltage_above_on_threshold(self, voltage: float) -> bool:
        """
        Return if a given voltage is above the configured threshold for the
        high/on/rising voltage for this fixture.

        :raises ValueError: if no target voltage could be determined.
        """
        bk_target_voltage_threshold_rising = self.get_arg_covariant(self.fixture_arguments,
                                                                    'target_voltage_threshold_rising',
                                                                    0)
        bk_target_voltage = self.get_arg_covariant_or_fail(self.fixture_arguments, 'target_voltage')
        rising_threshold_voltage = bk_target_voltage - bk_target_voltage_threshold_rising
        return (True if voltage > rising_threshold_voltage else False)

    def is_volage_below_off_threshold(self, voltage: float) -> bool:
        """
        Deprecated misspelling. See :meth:`is_voltage_below_off_threshold` for correct method.
        """
        return self.is_voltage_above_on_threshold(voltage)

    def is_voltage_below_off_threshold(self, voltage: float) -> bool:
        """
        Return if a given voltage is below the configured threshold for the
        low/off/falling voltage for this fixture.
        """
        falling_threshold_voltage = self.get_arg_covariant(self.fixture_arguments,
                                                           'target_voltage_threshold_falling',
                                                           0)
        return (True if voltage < falling_threshold_voltage else False)

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+
    async def _get_display(self,
                           uart: AbstractAsyncSerial,
                           command_timeout: typing.Optional[float]) \
            -> typing.Tuple[typing.Tuple[float, float, int], int]:
        display, status = await self._do_command(uart, self.CommandGetDisplay, command_timeout)
        if status != 0 or display is None or len(display) < 8:
            return ((0, 0, self.ModeInvalid), status)
        else:
            try:
                voltage = int(display[0:4]) / 100.0
                current = int(display[4:8]) / 100.0
                mode = int(display[8])
                if mode != self.ModeCC and mode != self.ModeCV:
                    mode = self.ModeInvalid
                    status = -1

            except ValueError:
                mode = self.ModeInvalid
                voltage = 0
                current = 0
            return ((voltage, current, mode), status)

    async def _up_or_down(self, is_up: bool,
                          uart: AbstractAsyncSerial,
                          args: nanaimo.Namespace,
                          inout_artifacts: nanaimo.Artifacts) -> None:
        start_time = uart.time()
        _, inout_artifacts.result_code = await self._do_command(uart,
                                                                (self.CommandTurnOn if is_up else self.CommandTurnOff),
                                                                args.bk_command_timeout)
        if inout_artifacts.result_code == 0 and args.bk_target_voltage is not None:
            wait_timeout = (None if args.bk_command_timeout is None
                            else max(0, args.bk_command_timeout - (uart.time() - start_time)))
            inout_artifacts.result_code = await self._wait_for_voltage(uart,
                                                                       wait_timeout,
                                                                       is_up)

    async def _do_command_from_args(self,
                                    uart: AbstractAsyncSerial,
                                    args: nanaimo.Namespace) -> nanaimo.Artifacts:
        artifacts = nanaimo.Artifacts(-1)

        if args.bk_command == '1':
            await self._up_or_down(True, uart, args, artifacts)
        elif args.bk_command == '0':
            await self._up_or_down(False, uart, args, artifacts)
        elif args.bk_command == 'r':
            _, artifacts.result_code = await self._do_command(uart, '\r\r\r\r', args.bk_command_timeout)
        elif args.bk_command == '?':
            display, artifacts.result_code = await self._get_display(uart, args.bk_command_timeout)
            if artifacts.result_code == 0:
                setattr(artifacts, 'display', display)
                setattr(artifacts, 'display_text', '{},{},{}'.format(
                    display[0], display[1], self.mode_to_text(int(display[1]))))
        else:
            self.logger.warning('command {} is not a valid Series1900BUart command.'.format(args.bk_command))

        return artifacts

    async def _wait_for_response(self,
                                 uart: AbstractAsyncSerial,
                                 command: str,
                                 puttime_secs: float,
                                 command_timeout: typing.Optional[float]) -> typing.Tuple[str, int]:
        start_time = uart.time()
        previous_line = None
        status = 1
        while True:
            now = uart.time()
            if command_timeout is not None and now - start_time > command_timeout:
                raise asyncio.TimeoutError()
            if self._debug:
                self.logger.debug('Waiting for response to command %s put before time %f seconds',
                                  command, puttime_secs)
            get_line_timeout_seconds = (command_timeout - (now - start_time) if command_timeout is not None else None)
            received_line = await uart.get_line(get_line_timeout_seconds)
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

    async def _do_command(self,
                          uart: AbstractAsyncSerial,
                          command: str,
                          command_timeout: typing.Optional[float]) -> typing.Tuple[str, int]:
        try:
            command_help = self.CommandHelp[command]
            is_command = True
            self.logger.debug('Sending command %s (help=%s)', command, command_help)
        except KeyError:
            self.logger.debug('Sending characters %s', re.sub('\\r', '<cr>', command))
            is_command = False

        puttime_secs = await uart.put_line(command + '\r')
        if is_command:
            return await self._wait_for_response(uart, command, puttime_secs, command_timeout)
        else:
            return ('', 1)

    async def _wait_for_voltage(self,
                                uart: AbstractAsyncSerial,
                                command_timeout: typing.Optional[float],
                                is_rising: bool) -> int:
        start_time = uart.time()
        while True:
            if command_timeout is not None and uart.time() - start_time > command_timeout:
                raise asyncio.TimeoutError()
            display_tuple, result = await self._get_display(uart, command_timeout)
            voltage = display_tuple[0]
            if result == 0:
                if is_rising and self.is_voltage_above_on_threshold(voltage):
                    self.logger.debug('---------------POWER SUPPLY UP----------------')
                    break
                elif not is_rising and self.is_voltage_below_off_threshold(voltage):
                    self.logger.debug('--------------POWER SUPPLY DOWN---------------')
                    break
            await asyncio.sleep(.01)
        return result


def pytest_nanaimo_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
    return Series1900BUart
