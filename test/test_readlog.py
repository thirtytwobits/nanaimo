#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import fixtures
import pytest
import asyncio
import pathlib
import nanaimo.file
import typing


@pytest.fixture
def paths_for_test():  # type: ignore
    return fixtures.Paths(__file__)


@pytest.mark.asyncio
@pytest.mark.timeout(15)
async def test_log_reader(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    dummy_log_file = (paths_for_test.out_dir / pathlib.Path(paths_for_test.test_name).with_suffix('.log'))

    simulated_file_logger = fixtures.simulators.FileLogger(
        paths_for_test.long_text,
        dummy_log_file,
        .05,
        echo=False)

    with simulated_file_logger:

        await simulated_file_logger.wait_for_file()

        reader = nanaimo.file.LogFile(dummy_log_file)
        line_count = 0

        async for line in reader.tail():
            line_count += 1
            print('{:5} :{}'.format(line_count, line), end='')
            if line_count >= 125:
                reader.cancel_tail()
