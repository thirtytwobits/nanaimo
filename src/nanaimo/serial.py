#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import concurrent.futures
import queue
import types
import typing

import serial


class ConcurrentUartMonitor:
    """
    Buffers serial input on another thread and provides line-oriented data
    from the tty via a synchronized queue.
    """
    TIMEOUT_SEC = 1
    LINE_BUFFER_SIZE = 255

    @classmethod
    def new_default(cls, port: str, baudrate: int) -> 'ConcurrentUartMonitor':
        return cls(serial.Serial(port=port, baudrate=baudrate, timeout=cls.TIMEOUT_SEC))

    def __init__(self, serial_port: serial.Serial) -> None:
        self._s = serial_port
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._buffer = queue.Queue(self.LINE_BUFFER_SIZE)  # type: queue.Queue[str]
        self._running = True
        self._serial_future = None  # type: typing.Optional[concurrent.futures.Future]
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
                        self._buffer.put(decoded_line, block=True, timeout=.500)
                        break
                    except queue.Full:
                        self._full_events += 1
