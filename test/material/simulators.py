#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import asyncio
import ctypes
import multiprocessing
import os
import pathlib
import threading
import types
import typing


class Serial:

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def is_open(self) -> bool:
        return True

    def flush(self) -> None:
        pass

    def cancel_read(self) -> None:
        with self._read_condition:
            self._read_condition.notify()

    @property
    def timeout(self) -> float:
        return self._timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        self._timeout = value

    def __init__(self, fake_data: typing.List[str], fake_eol: str = '\r\n', loop_fake_data: bool = True):
        super().__init__()
        self._timeout = 10.0
        self._fake_data = fake_data
        self._eol = fake_eol
        self._fake_data_index = 0
        self._fake_data_offset = 0
        self._loop_fake_data = loop_fake_data
        self._read_condition = threading.Condition()
        self._lines_written = 0
        self._lines_received = 0

    def reset_fake_input(self) -> None:
        self._fake_data_index = 0
        self._fake_data_offset = 0

    def read(self) -> bytes:
        while True:
            if self._fake_data_index >= len(self._fake_data):
                if self._loop_fake_data:
                    self._fake_data_index = 0
                    self._fake_data_offset = 0
                else:
                    with self._read_condition:
                        self._read_condition.wait()
                    return b''
            fake_line = self._fake_data[self._fake_data_index] + self._eol
            if self._fake_data_offset >= len(fake_line):
                self._fake_data_index += 1
                self._fake_data_offset = 0
            else:
                break

        return_char = fake_line[self._fake_data_offset]
        if return_char == self._eol:
            self._lines_received += 1
            with self._read_condition:
                # Put a little speed bump for each line.
                self._read_condition.wait(timeout=.01)

        return_bytes = return_char.encode('utf-8')
        self._fake_data_offset += 1
        return return_bytes

    def write(self, data: bytes) -> None:
        text = data.decode('utf-8')
        self._lines_written += text.count(self._eol)


class FileLogger:
    """
    Test fixture that provides a simulated, line-oriented log file written by a separate process.
    """

    class LogSpec(ctypes.Structure):
        _fields_ = [
            ('src', ctypes.c_wchar_p),
            ('dst', ctypes.c_wchar_p),
            ('cadence_seconds', ctypes.c_float),
            ('echo', ctypes.c_bool)
        ]

    def __init__(self, dummy_source: pathlib.Path, log_file: pathlib.Path, cadence_seconds: float, echo: bool = False):
        self._write_condition = multiprocessing.Condition()
        self._log_file = log_file
        self._run = multiprocessing.Value('i', 1)
        args = multiprocessing.Array(self.LogSpec,
                                     [(str(dummy_source), str(log_file), cadence_seconds, echo)])
        self._write_process = multiprocessing.Process(target=self._write_log,
                                                      args=(self._write_condition, self._run, args))

    async def wait_for_file(self) -> None:
        while not self._log_file.exists():
            await asyncio.sleep(.1)

    def __enter__(self) -> 'FileLogger':
        self._write_process.start()
        return self

    def __exit__(self,
                 # for python3.6+ this should be typing.Optional[typing.Type]
                 exception_type: typing.Optional[typing.Any],
                 exception_value: typing.Optional[typing.Any],
                 traceback: typing.Optional[types.TracebackType]) -> None:
        self._run.value = 0
        with self._write_condition:
            self._write_condition.notify()
        self._write_process.join()
        os.remove(self._log_file)

    @staticmethod
    def _write_log(write_condition, run, args):  # type: ignore
        line_count = 0
        source_file = args[0].src
        log_file = args[0].dst
        cadence_seconds = args[0].cadence_seconds
        echo = args[0].echo
        with open(source_file, 'r') as source:
            with open(log_file, 'w') as dest:
                while run.value == 1:
                    source_line = source.readline()
                    if echo:
                        print("{:5}: {}".format(line_count, source_line), end='')
                    line_count += 1
                    dest.write(source_line)
                    with write_condition:
                        write_condition.wait(cadence_seconds)
