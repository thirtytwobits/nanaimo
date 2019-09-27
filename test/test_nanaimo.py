#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import argparse
import asyncio
import os

import pytest

import fixtures
import fixtures.simulators
import nanaimo
import nanaimo.gtest
import nanaimo.jlink
import nanaimo.serial


@pytest.mark.timeout(10)
def test_uart_monitor() -> None:
    """
    Verify the nanaimo.ConcurrentUart class using a mock serial port.
    """
    serial = fixtures.simulators.Serial(fixtures.FAKE_TEST_SUCCESS)
    last_line = fixtures.FAKE_TEST_SUCCESS[-1]
    with nanaimo.serial.ConcurrentUart(serial) as monitor:
        while True:
            line = monitor.readline()
            if line is None:
                os.sched_yield()
                continue
            elif line == last_line:
                break


@pytest.mark.asyncio
async def test_program_uploader() -> None:
    uploader = nanaimo.jlink.ProgramUploaderJLink(fixtures.get_mock_JLinkExe())
    assert 0 == await uploader.upload(fixtures.get_s32K144_jlink_script())


@pytest.mark.asyncio
async def test_program_uploader_failure() -> None:
    uploader = nanaimo.jlink.ProgramUploaderJLink(fixtures.get_mock_JLinkExe(), ['--simulate-error'])
    assert 0 != await uploader.upload(fixtures.get_s32K144_jlink_script())


@pytest.mark.asyncio
async def test_program_while_monitoring() -> None:
    scripts = fixtures.get_s32K144_jlink_scripts()
    uploader = nanaimo.jlink.ProgramUploaderJLink(fixtures.get_mock_JLinkExe())
    serial = fixtures.simulators.Serial(fixtures.FAKE_TEST_SUCCESS)
    uploads = 0
    with nanaimo.serial.ConcurrentUart(serial) as monitor:
        for script in scripts:
            serial.reset_fake_input()
            results = await asyncio.gather(
                nanaimo.gtest.Parser(10).read_test(monitor),
                uploader.upload(script)
            )
            assert 2 == len(results)

            for result in results:
                assert 0 == result
            uploads += 1
    assert uploads > 1


@pytest.mark.asyncio
async def test_failed_test() -> None:
    serial = fixtures.simulators.Serial(fixtures.FAKE_TEST_FAILURE)
    with nanaimo.serial.ConcurrentUart(serial) as monitor:
        assert 1 == await nanaimo.gtest.Parser(10).read_test(monitor)


@pytest.mark.asyncio
async def test_timeout_while_monitoring() -> None:
    serial = fixtures.simulators.Serial(['gibberish'], loop_fake_data=False)
    with nanaimo.serial.ConcurrentUart(serial) as monitor:
        assert 0 != await nanaimo.gtest.Parser(4.0).read_test(monitor)


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks(event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Test the observe_tasks method of NanaimoTest
    """

    subject = fixtures.DummyNanaimoTest(event_loop)

    async def evaluating() -> int:
        return 0

    async def running() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    result = await subject.observe_tasks(evaluating(),
                                         0,
                                         True,
                                         running())
    assert len(result) == 1
    should_be_running = result.pop()

    assert not should_be_running.done()

    assert 1 == await should_be_running


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks_failure(event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Test the observe_tasks method of NanaimoTest where the running tasks exit.
    """

    subject = fixtures.DummyNanaimoTest(event_loop)

    async def evaluating() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    async def running() -> int:
        return 1

    with pytest.raises(nanaimo.AssertionError):
        await subject.observe_tasks(evaluating(),
                                    0,
                                    True,
                                    running())


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks_failure_no_assert(event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Test the observe_tasks method of NanaimoTest where the running tasks exit but without throwing
    an assertion error.
    """

    subject = fixtures.DummyNanaimoTest(event_loop)

    async def evaluating() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    async def running() -> int:
        return 1

    result = await subject.observe_tasks(evaluating(),
                                         0,
                                         False,
                                         running())

    assert 0 == len(result)


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks_timeout(event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Test the observe_tasks method of NanaimoTest where the running tasks do not exit.
    """

    subject = fixtures.DummyNanaimoTest(event_loop)

    async def evaluating() -> int:
        while True:
            await asyncio.sleep(1)

    async def running() -> int:
        while True:
            await asyncio.sleep(1)

    with pytest.raises(asyncio.TimeoutError):
        await subject.observe_tasks(evaluating(),
                                    1,
                                    True,
                                    running())


@pytest.mark.timeout(20)
@pytest.mark.asyncio
async def test_countdown_sleep(event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Test the observe_tasks method of NanaimoTest where the running tasks do not exit.
    """
    subject = fixtures.DummyNanaimoTest(event_loop)

    await subject.countdown_sleep(5.3)
