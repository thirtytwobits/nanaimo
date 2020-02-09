#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import pathlib
import re

import pytest

import nanaimo
import nanaimo.fixtures


@pytest.mark.asyncio
async def test_subprocess_match_filter(mock_JLinkExe: pathlib.Path) -> None:
    """
    Executing JLinkExe breaks subprocess output stream filtering.
    We replicate this by searching the output for a simple error
    which appears in stdout from JLinkExe when run from a shell, but
    is missing when run as a SubprocessFixture command:
    """
    class TestSubprocessFixture(nanaimo.fixtures.SubprocessFixture):
        argument_prefix = 'test'

        def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
            return '{} --simulate-error'.format(str(mock_JLinkExe))

    subprocess_fixture = TestSubprocessFixture(nanaimo.fixtures.FixtureManager())
    filter = nanaimo.fixtures.SubprocessFixture.SubprocessMessageMatcher(re.compile('Simulating abnormal exit.'))
    subprocess_fixture.stdout_filter = filter
    subprocess_fixture.stderr_filter = filter
    await subprocess_fixture.gather(test_log_stdout=True)
    assert filter.match_count == 1
