#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import serial
import concurrent.futures
import typing
import types
import asyncio
import queue
import pathlib


class ConcurrentUartMonitor:

    TIMEOUT_SEC = 1
    LINE_BUFFER_SIZE = 100

    @classmethod
    def new_default(cls, port: str, baudrate: int) -> 'ConcurrentUartMonitor':
        return cls(serial.Serial(port=port, baudrate=baudrate, timeout=cls.TIMEOUT_SEC))

    def __init__(self, serial_port: serial.Serial) -> None:
        self._s = serial_port
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._buffer: queue.Queue[str] = queue.Queue(self.LINE_BUFFER_SIZE)
        self._running = True
        self._serial_future: typing.Optional[concurrent.futures.Future] = None

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
            try:
                data = self._serial_future.result()
            except Exception as exc:
                print('generated an exception: %s' % (exc))
            else:
                print('page is %d bytes' % (len(data)))
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
            try:
                self._buffer.put(self._s.readline(), block=True, timeout=1)
            except queue.Full:
                pass


class GTestParser:
    """
    TODO: run UART through this class and emit events.
    """
    pass


class ProgramUploader:

    def __init__(self, jlink_script: pathlib.Path):
        self._jlink_exe = 'JLinkExe'
        self._jlink_script = jlink_script

    async def upload(self) -> None:
        # JLinkExe -CommanderScript test_math_saturation_loadfile_swd.jlink
        cmd = '{} {}'.format(self._jlink_exe, self._jlink_script)
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        print(f'[{cmd!r} exited with {proc.returncode}]')
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')
