#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import argparse
import asyncio
import codecs
import concurrent.futures
import logging
import queue
import re
import threading
import types
import typing

import serial


class TimestampedLine(str):

    @classmethod
    def create(cls, line_text: object, timestamp_seconds: float) -> 'TimestampedLine':
        timestamped = TimestampedLine(line_text)
        timestamped._timestamp_seconds = timestamp_seconds
        return timestamped

    def __init__(self, line_text: object):
        self._timestamp_seconds = 0.0

    @property
    def timestamp_seconds(self) -> float:
        return self._timestamp_seconds


class AbstractSerial:

    @classmethod
    def on_visit_argparse_subparser(cls, subparsers: argparse._SubParsersAction, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument('--port',
                               help='The port to monitor.')

        subparser.add_argument('--port-speed', '-b', help='the speed of the port (e.g. baud rate for serial ports).')


class AbstractAsyncSerial(AbstractSerial):

    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._loop = (loop if loop is not None else asyncio.get_event_loop())
        self._read_buffer = queue.Queue()  # type: queue.Queue[TimestampedLine]
        self._write_buffer = queue.Queue()  # type: queue.Queue[str]
        self._rx_decoder = codecs.getincrementaldecoder('UTF-8')('replace')
        self._tx_encoder = codecs.getincrementalencoder('UTF-8')('replace')
        self._queues_are_running = True

    def stop(self) -> None:
        self._queues_are_running = False

    def time(self) -> float:
        """
        Get the current, monotonic time, in fractional seconds, using the same
        clock used for receive timestamps.
        """
        return self._loop.time()

    # +-----------------------------------------------------------------------+
    # | ASYNC OPERATIONS
    # +-----------------------------------------------------------------------+
    async def get_line(self, timeout_seconds: float = 0) -> TimestampedLine:
        start_time = self.time()
        while True:
            try:
                return self._read_buffer.get_nowait()
            except queue.Empty:
                if not self._queues_are_running:
                    raise
                if timeout_seconds > 0 and self.time() - start_time > timeout_seconds:
                    raise asyncio.TimeoutError()
                await asyncio.sleep(0.001)

    async def put_line(self, input_line: str, end: typing.Optional[str] = None, timeout_seconds: float = 0) -> float:
        start_time = self.time()
        while self._queues_are_running:
            try:
                start_of_put = self.time()
                self._write_buffer.put_nowait(input_line)
                return start_of_put
            except queue.Full:
                if timeout_seconds > 0 and self.time() - start_time > timeout_seconds:
                    raise asyncio.TimeoutError()
                await asyncio.sleep(0.001)
        return self.time()


class ConcurrentUart(AbstractAsyncSerial):
    """
    Buffers serial input on another thread and provides line-oriented access
    to/from the tty via synchronized queues.
    """
    DefaultSerialTimeoutSeconds = 1
    WriteBufferEndOfTransmission = '\4'

    @classmethod
    def new_default(cls, port: str, baudrate: int, loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> 'ConcurrentUart':
        return cls(serial.Serial(port=port, baudrate=baudrate, timeout=cls.DefaultSerialTimeoutSeconds), loop)

    def __init__(self, serial_port: serial.Serial, loop: typing.Optional[asyncio.AbstractEventLoop] = None, eol: str = '\r\n', echo: bool = False) -> None:
        super().__init__(loop)
        self._s = serial_port
        self._echo = echo
        self._eol = eol
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._serial_futures = []  # type: typing.List[concurrent.futures.Future]
        self._full_events = 0
        self._logger_tx = logging.getLogger(type(self).__name__ + "_tx")
        self._logger_rx = logging.getLogger(type(self).__name__ + "_rx")

    @property
    def buffer_full_events(self) -> int:
        return self._full_events

    @property
    def serial_port(self) -> serial.Serial:
        return self._s

    @property
    def eol(self) -> str:
        return self._eol

    @eol.setter
    def eol(self, eol: str) -> None:
        self._eol = eol

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def echo(self) -> bool:
        return self._echo

    @echo.setter
    def echo(self, value: bool) -> None:
        self._echo = value

    @property
    def timeout_seconds(self) -> float:
        return float(self._s.timeout)

    @timeout_seconds.setter
    def timeout_seconds(self, value: float) -> None:
        self._s.timeout = value

    # +-----------------------------------------------------------------------+
    # | CONTEXT MANAGER
    # +-----------------------------------------------------------------------+

    def __enter__(self) -> 'ConcurrentUart':
        if not self._s.is_open:
            self._s.open()
        self._serial_futures.append(self._executor.submit(self._buffer_input))
        self._serial_futures.append(self._executor.submit(self._buffer_output))

        return self

    def __exit__(self,
                 exception_type: typing.Optional[typing.Any],  # for python3.6+ this should be typing.Optional[typing.Type]
                 exception_value: typing.Optional[typing.Any],
                 traceback: typing.Optional[types.TracebackType]) -> None:
        self.stop()
        self._s.flush()
        self._s.cancel_read()
        self._write_buffer.put_nowait(self.WriteBufferEndOfTransmission)
        for serial_future in reversed(self._serial_futures):
            if not serial_future.done():
                serial_future.result((self._s.timeout if self._s.timeout > 0 else None))
        self._s.close()
        self._executor.shutdown(wait=True)

    # +-----------------------------------------------------------------------+
    # | CONCURRENT OPERATIONS
    # +-----------------------------------------------------------------------+

    def readline(self) -> typing.Optional[TimestampedLine]:
        try:
            return self._read_buffer.get_nowait()
        except queue.Empty:
            return None

    def writeline(self, input_line: str, end: typing.Optional[str] = None) -> float:
        try:
            self._write_buffer.put_nowait(input_line + (end if end is not None else self._eol))
            return self.time()
        except queue.Full:
            return False

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+

    def _buffer_input(self) -> None:
        try:
            local_storage = threading.local()
            local_storage.line_buffer = ''
            while self._queues_are_running:
                self._buffer_input_step(local_storage)
        finally:
            if self._queues_are_running:
                self._logger_rx.error("read thread exiting.")
            self._queues_are_running = False

    def _buffer_input_step(self, local_storage: threading.local) -> None:
        raw_input = self._s.read()
        rx_timestamp_seconds = self.time()
        decoded_input = local_storage.line_buffer + self._rx_decoder.decode(raw_input)
        local_storage.line_buffer = ''
        decoded_lines = decoded_input.split(self._eol)
        if not decoded_input.endswith(self._eol) and len(decoded_lines) > 0:
            # last bit didn't yet have a terminator. Buffer it for the next
            # go around
            local_storage.line_buffer = decoded_lines[-1]
            decoded_lines = decoded_lines[:-1]
        for decoded_line in decoded_lines:
            try:
                timestamped_line = TimestampedLine.create(decoded_line, rx_timestamp_seconds)
                self._read_buffer.put_nowait(timestamped_line)
                self._logger_rx.debug(re.sub('\\r', '<cr>', timestamped_line))
            except queue.Full:
                self._logger_rx.warn("read buffer overflow.")
                self._full_events += 1

    def _buffer_output(self) -> None:
        try:
            while self._queues_are_running:
                self._buffer_output_step()
        finally:
            if self._queues_are_running:
                self._logger_tx.error("write thread exiting.")
            self._queues_are_running = False

    def _buffer_output_step(self) -> None:
        try:
            writeline = self._write_buffer.get(block=True)
            if writeline != self.WriteBufferEndOfTransmission:
                self._s.write(self._tx_encoder.encode(writeline))
                if self._echo:
                    self._logger_tx.debug(re.sub('\\r', '<cr>', writeline))
        except queue.Empty:
            pass
