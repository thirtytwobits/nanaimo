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
"""
Connections are built-in async abstractions using standard communication
protocols like UART, I2C, CAN, TCP/IP, etc. :class:`Instrument` and :class:`nanaimo.fixtures.Fixture`
classes use connections to bind to physical hardware.
"""
import asyncio
import codecs
import queue
import typing

import nanaimo


class TimestampedLine(str):
    """
    A line of text with an associated timestamp. This is a subclass of string so the
    object may be treated as a string without conversion.
    """

    @classmethod
    def create(cls, line_text: object, timestamp_seconds: float) -> 'TimestampedLine':
        timestamped = TimestampedLine(line_text)
        timestamped._timestamp_seconds = timestamp_seconds
        return timestamped

    def __init__(self, line_text: object):
        self._timestamp_seconds = 0.0

    @property
    def timestamp_seconds(self) -> float:
        """
        The timestamp for the line in fractional seconds. For example, this would be the time
        the line of text was received when this type is returned for a getter.
        """
        return self._timestamp_seconds


class AbstractSerial:
    """
    Abstract base class for a serial communication channel.
    """

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--port',
                               help='The port to monitor.')

        arguments.add_argument('--port-speed',
                               default=9600,
                               help='the speed of the port (e.g. baud rate for serial ports).')


class AbstractAsyncSerial(AbstractSerial):
    """
    Abstract base class for a serial communication channel that provides
    asynchronous methods.
    """

    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._loop = (loop if loop is not None else asyncio.get_event_loop())
        self._read_buffer = queue.Queue()  # type: queue.Queue[TimestampedLine]
        self._write_buffer = queue.Queue()  # type: queue.Queue[str]
        self._rx_decoder = codecs.getincrementaldecoder('UTF-8')('replace')
        self._tx_encoder = codecs.getincrementalencoder('UTF-8')('replace')
        self._queues_are_running = True
        self._rx_buffer_overflows = 0

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def rx_buffer_overflows(self) -> int:
        return self._rx_buffer_overflows

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
    async def get_line(self, timeout_seconds: typing.Optional[float] = None) -> TimestampedLine:
        """
        Get a line of text.

        :param float timeout_seconds: Time in fractional seconds to wait for input.
        :returns: A line of text with the time it was received at.
        :rtype: TimestampedLine
        :raises asyncio.TimeoutError: If a full line of text was not received within
            the specified timeout period.
        """
        start_time = self.time()
        while True:
            try:
                return self._read_buffer.get_nowait()
            except queue.Empty:
                if not self._queues_are_running:
                    raise
                if timeout_seconds is not None and self.time() - start_time > timeout_seconds:
                    raise asyncio.TimeoutError()
                await asyncio.sleep(0.001)

    async def put_line(self, input_line: str, timeout_seconds: typing.Optional[float] = None) -> float:
        """
        Put a line of text to the serial device.

        :param str input_line: The line to put.
        :param float timeout_seconds: Fractional seconds to block for if the input buffer is full. If the buffer does
            not become available within this time then :class:`asyncio.TimeoutError` is raised. Use 0 to block
            forever.
        :return: The monotonic system time that the line was put into the serial buffers at (see :meth:`time`).
        :raises asyncio.TimeoutError: If an input buffer did not become available within the specified timeout.
        """
        start_time = self.time()
        while self._queues_are_running:
            try:
                start_of_put = self.time()
                self._write_buffer.put_nowait(input_line)
                return start_of_put
            except queue.Full:
                if timeout_seconds is not None and self.time() - start_time > timeout_seconds:
                    raise asyncio.TimeoutError()
                await asyncio.sleep(0.001)
        return self.time()
