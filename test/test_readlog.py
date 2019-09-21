#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import fixtures
import pytest
import asyncio
import pathlib


@pytest.fixture
def paths_for_test():  # type: ignore
    return fixtures.Paths(__file__)


@pytest.mark.asyncio
async def test_log_reader(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    simulated_logfile = fixtures.simulators.Logfile(
        event_loop,
        paths_for_test.long_text,
        (paths_for_test.out_dir / pathlib.Path(paths_for_test.test_name).with_suffix('.log')))

    simulated_process = fixtures.simulators.Process(event_loop)

    await asyncio.wait_for(
        asyncio.gather(
            simulated_process.run(4.0, 0),
            simulated_logfile.run(0.100, simulated_process.future),
            loop=event_loop
        ),
        30.0,
        loop=event_loop
    )
