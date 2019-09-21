#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import nanaimo.serial
import asyncio
import typing
import logging
import re


class Series1900BUart:
    """
    Control of a 1900B series BK Precision power supply via UART.
    """

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

    def __init__(self,
                 uart: nanaimo.serial.ConcurrentUart,
                 command_timeout_seconds: float):
        self._uart = uart
        self._uart.eol = '\r'
        self._command_timeout_seconds = command_timeout_seconds
        self._uart.timeout_seconds = command_timeout_seconds
        self._logger = logging.getLogger(type(self).__name__)

    async def send_command(self, command: str) -> typing.Optional[typing.Any]:
        if command == '1':
            return await self._do_command(self.CommandTurnOn)
        elif command == '0':
            return await self._do_command(self.CommandTurnOff)
        elif command == 'r':
            return await self._do_command('\r\r\r\r')
        elif command == '?':
            return await self._do_command(self.CommandGetDisplay)
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

        puttime_secs = await self._uart.put_line((self._uart.eol * 2) + command + self._uart.eol)
        previous_line = None
        if is_command:
            start_time = self._uart.time()
            while True:
                now = self._uart.time()
                if now - start_time > self._command_timeout_seconds:
                    raise asyncio.TimeoutError()
                self._logger.debug('Waiting for response to command %s put before time %f seconds', command, puttime_secs)
                received_line = await self._uart.get_line(self._command_timeout_seconds - (now - start_time))
                self._logger.debug('At %f Got line: %s', received_line.timestamp_seconds, received_line)
                # The result has to be from after the put or
                # it's an old result from a buffer.
                if received_line.timestamp_seconds > puttime_secs and received_line == self.ResultOk:
                    break
                # Skip any empty lines the device sends back.
                if len(received_line) > 0:
                    previous_line = received_line
        return previous_line
