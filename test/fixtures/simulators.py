#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import typing
import pathlib
import asyncio


class Serial:

    def __init__(self, fake_data: typing.List[str]):
        self._fake_data = fake_data
        self._fake_data_index = 0

    def reset_mock(self) -> None:
        self._fake_data_index = 0

    def readline(self) -> typing.Optional[bytes]:
        line = None
        try:
            line = self._fake_data[self._fake_data_index]
            self._fake_data_index += 1
        except IndexError:
            pass
        if line is not None:
            return bytearray(line, 'utf-8')
        else:
            return bytearray()


class Logfile:
    """
    Test fixture that provides a simulated, line-oriented log file.
    """
    RequiredEncoding = 'utf-8'

    def __init__(self, loop: asyncio.AbstractEventLoop, source_file: pathlib.Path, dest_file: pathlib.Path):
        self._loop = loop
        self._source_file = source_file
        self._dest_file = dest_file

    async def run(self, cadence_seconds: float, run_until: asyncio.Future) -> None:
        """
        Copies source file to dest file line-by-line sleeping
        for :param:`cadence_seconds` between each line.
        :param pathlib.Path cadence_seconds: The amount of time to wait between writing each line of code.
        :param asyncio.Future run_until: Run will continue until this future is marked as done.
        """
        if run_until.done():
            # Don't create the dest file if the future is already done.
            return
        with open(self._dest_file, 'w', encoding=self.RequiredEncoding) as dest_file:
            print('Writing to logfile {}'.format(self._dest_file))
            while not run_until.done():
                # Continually read from the source until done. If we get to the end of the source
                # start over from the beginning.
                with open(self._source_file, 'r', encoding=self.RequiredEncoding) as source_file:
                    while not run_until.done():
                        next_line = source_file.readline()
                        if next_line is None:
                            await asyncio.sleep(cadence_seconds, loop=self._loop)
                            break
                        dest_file.write(next_line)
                        print(next_line, end='')
                        await asyncio.sleep(cadence_seconds, loop=self._loop)


class Process:
    """
    Object that fake out the Nanaimo process pattern.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self.future = loop.create_future()

    async def run(self, run_for_seconds: float, result: typing.Any) -> None:
        await asyncio.sleep(run_for_seconds, loop=self._loop)
        self.future.set_result(result)
