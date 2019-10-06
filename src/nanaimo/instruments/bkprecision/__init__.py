#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import asyncio
import contextlib
import logging
import pathlib
import re
import typing

from nanaimo.connections.uart import ConcurrentUart as Uart


class Series1900BUart:
    """
    Control of a 1900B series BK Precision power supply via UART.
    """

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

    @classmethod
    @contextlib.contextmanager
    def default_configuration(cls, port: typing.Union[str, pathlib.Path]) -> typing.Generator['Series1900BUart', None, None]:
        with Uart.new_default(str(port), 9600) as bk_uart:
            bk = cls(bk_uart, cls.DefaultCommandTimeoutSeconds)
            yield bk

    def __init__(self,
                 uart: Uart,
                 command_timeout_seconds: float = 0,
                 debug: bool = False):
        self._uart = uart
        self._uart.eol = '\r'
        self._command_timeout_seconds = command_timeout_seconds
        self._uart.timeout_seconds = command_timeout_seconds
        self._logger = logging.getLogger(type(self).__name__)
        self._debug = debug

    async def send_command(self, command: str) -> typing.Optional[typing.Any]:
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
        if command == '1':
            return await self._do_command(self.CommandTurnOn)
        elif command == '0':
            return await self._do_command(self.CommandTurnOff)
        elif command == 'r':
            return await self._do_command('\r\r\r\r')
        elif command == '?':
            voltage, current, status = await self.get_display()
            return '{},{},{}'.format(voltage, current, ('ON' if status else 'OFF'))
        else:
            raise ValueError('command {} is not a valid Series1900BUart command.'.format(command))

    async def turn_on(self) -> None:
        await self._do_command(self.CommandTurnOn)

    async def turn_off(self) -> None:
        await self._do_command(self.CommandTurnOff)

    async def get_display(self) -> typing.Tuple[float, float, int]:
        display = await self._do_command(self.CommandGetDisplay)
        if display is None or len(display) < 8:
            raise RuntimeError('Failed to obtain a voltage.')
        voltage = int(display[0:4]) / 100.0
        current = int(display[4:8]) / 100.0
        status = int(display[8])
        return (voltage, current, status)

    async def _do_command(self, command: str) -> typing.Optional[typing.Any]:
        try:
            command_help = self.CommandHelp[command]
            is_command = True
            self._logger.debug('Sending command %s (help=%s)', command, command_help)
        except KeyError:
            self._logger.debug('Sending characters %s', re.sub('\\r', '<cr>', command))
            is_command = False

        puttime_secs = await self._uart.put_line(command + self._uart.eol)
        previous_line = None
        if is_command:
            start_time = self._uart.time()
            while True:
                now = self._uart.time()
                if self._command_timeout_seconds > 0 and now - start_time > self._command_timeout_seconds:
                    raise asyncio.TimeoutError()
                if self._debug:
                    self._logger.debug('Waiting for response to command %s put before time %f seconds', command, puttime_secs)
                received_line = await self._uart.get_line((self._command_timeout_seconds - (now - start_time) if self._command_timeout_seconds > 0 else 0))
                if self._debug:
                    self._logger.debug('At %f Got line: %s', received_line.timestamp_seconds, received_line)
                # The result has to be from after the put or
                # it's an old result from a buffer.
                if received_line.timestamp_seconds > puttime_secs and received_line == self.ResultOk:
                    break
                # Skip any empty lines the device sends back.
                if len(received_line) > 0:
                    previous_line = received_line
        return previous_line

    async def wait_for_voltage(self, is_min: bool, threshold_v: float) -> None:
        while True:
            display_tuple = await self.get_display()
            voltage = display_tuple[0]
            if (voltage >= threshold_v if is_min else voltage <= threshold_v):
                if is_min:
                    self._logger.debug('---------------POWER SUPPLY UP----------------')
                else:
                    self._logger.debug('--------------POWER SUPPLY DOWN---------------')
                break
            await asyncio.sleep(.1)
