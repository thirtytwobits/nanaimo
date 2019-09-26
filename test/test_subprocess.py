#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import asyncio
import sys
import typing

import pytest

import fixtures


@pytest.fixture
def paths_for_test():  # type: ignore
    return fixtures.Paths(__file__)


class DummyProtocol(asyncio.SubprocessProtocol):

    def __init__(self, exit_future: asyncio.Future):
        self.exit_future = exit_future
        self._count = 0

    def pipe_data_received(self, fd: int, data: typing.Union[bytes, str]) -> None:
        print(data.decode('utf-8'))
        self._count += 1

    def process_exited(self) -> None:
        self.exit_future.set_result(True)


@pytest.mark.asyncio
@pytest.mark.timeout(15)
async def test_continuous_subprocess(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    exit_future = asyncio.Future(loop=event_loop)  # type: typing.Future

    code = """
import sys
with open('{}', 'r') as log_file:
    while True:
        line = log_file.readline()
        if line:
            sys.stdout.write(line)
""".format(str(paths_for_test.long_text))

    transport, protocol = await event_loop.subprocess_exec(lambda: DummyProtocol(exit_future),
                                                           sys.executable,
                                                           '-c',
                                                           code,
                                                           stdin=asyncio.subprocess.PIPE)

    try:
        await asyncio.wait_for(exit_future, 1)
    except asyncio.TimeoutError:
        pass

    transport.close()
