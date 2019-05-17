#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import asyncio
import concurrent.futures
import logging
import pathlib
import queue
import re
import time
import types
import typing

import serial


class ConcurrentUartMonitor:

    TIMEOUT_SEC = 1
    LINE_BUFFER_SIZE = 255

    @classmethod
    def new_default(cls, port: str, baudrate: int) -> 'ConcurrentUartMonitor':
        return cls(serial.Serial(port=port, baudrate=baudrate, timeout=cls.TIMEOUT_SEC))

    def __init__(self, serial_port: serial.Serial) -> None:
        self._s = serial_port
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._buffer: queue.Queue[str] = queue.Queue(self.LINE_BUFFER_SIZE)
        self._running = True
        self._serial_future: typing.Optional[concurrent.futures.Future] = None
        self._full_events = 0

    @property
    def buffer_full_events(self) -> int:
        return self._full_events

    @property
    def serial_port(self) -> serial.Serial:
        return self._s

    # +-----------------------------------------------------------------------+
    # | CONTEXT MANAGER
    # +-----------------------------------------------------------------------+

    def __enter__(self) -> 'ConcurrentUartMonitor':
        self._serial_future = self._executor.submit(self._buffer_input)
        return self

    def __exit__(self,
                 exception_type: typing.Optional[typing.Type],
                 exception_value: typing.Optional[typing.Any],
                 traceback: typing.Optional[types.TracebackType]) -> None:
        self._running = False
        if self._serial_future is not None:
            self._serial_future.result()
        self._executor.shutdown(wait=True)

    # +-----------------------------------------------------------------------+
    # | CONCURRENT OPERATIONS
    # +-----------------------------------------------------------------------+

    def readline(self) -> typing.Optional[str]:
        try:
            return self._buffer.get_nowait()
        except queue.Empty:
            return None

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+

    def _buffer_input(self) -> None:
        while self._running:
            line = self._s.readline()
            if (len(line) > 0):
                decoded_line = line.decode('utf-8')
                if decoded_line.endswith('\n'):
                    decoded_line = decoded_line[:-1]
                while True:
                    try:
                        self._buffer.put(decoded_line, block=True, timeout=.1)
                        break
                    except queue.Full:
                        self._full_events += 1
                        time.sleep(.010)


class GTestParser:
    """
    Uses a given monitor to watch for google test results.
    """

    def __init__(self, timeout_seconds: float):
        self._logger = logging.getLogger(__name__)
        self._timeout_seconds = timeout_seconds
        self._completion_pattern = re.compile(r'\[\s*(PASSED|FAILED)\s*\]\s*(\d+)\s+tests.')

    async def read_test(self, uart: ConcurrentUartMonitor) -> int:
        start_time = time.monotonic()
        result = 1
        line_count = 0
        while True:
            if time.monotonic() - start_time > self._timeout_seconds:
                result = 2
                self._logger.warning('GTestParser timeout after %f seconds', time.monotonic() - start_time)
                break
            line = uart.readline()
            if line is None:
                await asyncio.sleep(.250)
                continue

            self._logger.debug(line)
            line_count += 1
            line_match = self._completion_pattern.match(line)
            if line_match is not None:
                result = (0 if line_match.group(1) == 'PASSED' else 1)
                break
        if 0 == result:
            self._logger.info('Detected successful test after %f seconds.', time.monotonic() - start_time)
        self._logger.debug('Processed %d lines. There were %d buffer full events reported.', line_count, uart.buffer_full_events)
        return result


class ProgramUploader:

    def __init__(self,
                 jlink_script: pathlib.Path,
                 jlink_executable: pathlib.Path = pathlib.Path('JLinkExe'),
                 extra_arguments: typing.Optional[typing.List[str]] = None):
        self._logger = logging.getLogger(__name__)
        self._jlink_exe = jlink_executable
        self._jlink_script = jlink_script
        self._extra_arguments = extra_arguments

    async def upload(self) -> int:
        cmd = '{} -CommanderScript {}'.format(self._jlink_exe, self._jlink_script)
        if self._extra_arguments is not None:
            cmd += ' ' + ' '.join(self._extra_arguments)

        self._logger.info('starting upload: %s', cmd)
        proc: asyncio.subprocess.Process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        self._logger.info('%s exited with %i', cmd, proc.returncode)

        if stdout:
            self._logger.debug(stdout.decode())
        if stderr:
            self._logger.error(stderr.decode())

        return proc.returncode
