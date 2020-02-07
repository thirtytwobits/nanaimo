#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import asyncio
import pathlib
import re
import sys
import typing

import pytest

import material
import nanaimo
import nanaimo.fixtures


class DummyProtocol(asyncio.SubprocessProtocol):

    def __init__(self, exit_future: asyncio.Future):
        self.exit_future = exit_future
        self._count = 0

    def pipe_data_received(self, fd: int, data: typing.Union[bytes, str]) -> None:
        print(typing.cast(bytes, data).decode('utf-8'))
        self._count += 1

    def process_exited(self) -> None:
        self.exit_future.set_result(True)


@pytest.mark.asyncio
@pytest.mark.timeout(15)
async def test_continuous_subprocess(paths_for_test: material.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    exit_future = asyncio.Future(loop=event_loop)  # type: typing.Any

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


@pytest.mark.asyncio
async def test_subprocess_match_filter(nanaimo_fixture_manager: nanaimo.fixtures.FixtureManager,
                                       mock_JLinkExe: pathlib.Path) -> None:
    """
    Executing JLinkExe breaks subprocess output stream filtering.
    We replicate this by searching the output for a simple error
    which appears in stdout from JLinkExe when run from a shell, but
    is missing when run as a SubprocessFixture command:
    """
    class TestSubprocessFixture(nanaimo.fixtures.SubprocessFixture):
        argument_prefix = 'test'

        def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
            return '{} -CommanderScript MISSING_FILE_'.format(str(mock_JLinkExe))

    subprocess_fixture = TestSubprocessFixture(nanaimo_fixture_manager)
    filter = nanaimo.fixtures.SubprocessFixture.SubprocessMessageMatcher(re.compile('Simulating normal exit.'))
    subprocess_fixture.stdout_filter = filter
    await subprocess_fixture.gather(test_log_stdout=True)
    assert filter.match_count == 1
