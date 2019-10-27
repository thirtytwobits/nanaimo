#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import argparse
import asyncio
import os
import pathlib
import typing
from unittest.mock import patch

import pytest

import fixtures.simulators
import nanaimo
import nanaimo.connections
import nanaimo.connections.uart
import nanaimo.instruments.jlink
import nanaimo.parsers.gtest


@pytest.mark.timeout(10)
def test_uart_monitor() -> None:
    """
    Verify the nanaimo.ConcurrentUart class using a mock serial port.
    """
    serial = fixtures.simulators.Serial(fixtures.FAKE_TEST_SUCCESS)
    last_line = fixtures.FAKE_TEST_SUCCESS[-1]
    with nanaimo.connections.uart.ConcurrentUart(serial) as monitor:
        while True:
            line = monitor.readline()
            if line is None:
                os.sched_yield()
                continue
            elif line == last_line:
                break


@pytest.mark.asyncio
async def test_program_uploader(mock_JLinkExe: pathlib.Path,
                                s32K144_jlink_script: pathlib.Path) -> None:
    uploader = nanaimo.instruments.jlink.ProgramUploaderJLink(mock_JLinkExe)
    assert 0 == await uploader.upload(s32K144_jlink_script)


@pytest.mark.asyncio
async def test_program_uploader_failure(mock_JLinkExe: pathlib.Path,
                                        s32K144_jlink_script: pathlib.Path) -> None:
    uploader = nanaimo.instruments.jlink.ProgramUploaderJLink(mock_JLinkExe, ['--simulate-error'])
    assert 0 != await uploader.upload(s32K144_jlink_script)


@pytest.mark.asyncio
async def test_program_while_monitoring(mock_JLinkExe: pathlib.Path,
                                        s32K144_jlink_scripts: typing.Iterator[pathlib.Path]) -> None:
    scripts = s32K144_jlink_scripts
    uploader = nanaimo.instruments.jlink.ProgramUploaderJLink(mock_JLinkExe)
    serial = fixtures.simulators.Serial(fixtures.FAKE_TEST_SUCCESS)
    uploads = 0
    with nanaimo.connections.uart.ConcurrentUart(serial) as monitor:
        for script in scripts:
            serial.reset_fake_input()
            results = await asyncio.gather(
                nanaimo.parsers.gtest.Parser(10).read_test(monitor),
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
    with nanaimo.connections.uart.ConcurrentUart(serial) as monitor:
        assert 1 == await nanaimo.parsers.gtest.Parser(10).read_test(monitor)


@pytest.mark.asyncio
async def test_timeout_while_monitoring() -> None:
    serial = fixtures.simulators.Serial(['gibberish'], loop_fake_data=False)
    with nanaimo.connections.uart.ConcurrentUart(serial) as monitor:
        assert 0 != await nanaimo.parsers.gtest.Parser(4.0).read_test(monitor)


@pytest.mark.timeout(10)
@pytest.mark.asyncio
@patch('nanaimo.FixtureManager')
async def test_observe_tasks(MockFixtureManager: typing.Any,
                             event_loop: asyncio.AbstractEventLoop,
                             dummy_nanaimo_fixture: nanaimo.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture
    """

    async def evaluating() -> int:
        return 0

    async def running() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    result = await dummy_nanaimo_fixture.observe_tasks_assert_not_done(evaluating(),
                                                                       0,
                                                                       running())
    assert len(result) == 1
    should_be_running = result.pop()

    assert not should_be_running.done()

    assert 1 == await should_be_running


@pytest.mark.timeout(10)
@pytest.mark.asyncio
@patch('nanaimo.FixtureManager')
async def test_observe_tasks_failure(MockFixtureManager: typing.Any,
                                     event_loop: asyncio.AbstractEventLoop,
                                     dummy_nanaimo_fixture: nanaimo.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks exit.
    """

    async def evaluating() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    async def running() -> int:
        return 1

    with pytest.raises(nanaimo.AssertionError):
        await dummy_nanaimo_fixture.observe_tasks_assert_not_done(evaluating(),
                                                                  0,
                                                                  running())


@pytest.mark.timeout(10)
@pytest.mark.asyncio
@patch('nanaimo.FixtureManager')
async def test_observe_tasks_failure_no_assert(MockFixtureManager: typing.Any,
                                               event_loop: asyncio.AbstractEventLoop,
                                               dummy_nanaimo_fixture: nanaimo.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks exit but without throwing
    an assertion error.
    """

    async def evaluating() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    async def running() -> int:
        return 1

    result = await dummy_nanaimo_fixture.observe_tasks(evaluating(),
                                                       0,
                                                       running())

    assert 0 == len(result)


@pytest.mark.timeout(10)
@pytest.mark.asyncio
@patch('nanaimo.FixtureManager')
async def test_observe_tasks_timeout(MockFixtureManager: typing.Any,
                                     event_loop: asyncio.AbstractEventLoop,
                                     dummy_nanaimo_fixture: nanaimo.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks do not exit.
    """

    async def evaluating() -> int:
        while True:
            await asyncio.sleep(1)

    async def running() -> int:
        while True:
            await asyncio.sleep(1)

    with pytest.raises(asyncio.TimeoutError):
        await dummy_nanaimo_fixture.observe_tasks_assert_not_done(evaluating(),
                                                                  1,
                                                                  running())


@pytest.mark.timeout(20)
@pytest.mark.asyncio
@patch('nanaimo.FixtureManager')
async def test_countdown_sleep(MockFixtureManager: typing.Any,
                               event_loop: asyncio.AbstractEventLoop,
                               dummy_nanaimo_fixture: nanaimo.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks do not exit.
    """
    await dummy_nanaimo_fixture.countdown_sleep(5.3)


def test_enable_default_from_environ(nanaimo_defaults: nanaimo.config.ArgumentDefaults) -> None:
    a = nanaimo.Arguments(argparse.ArgumentParser(), nanaimo_defaults)

    a.add_argument('yep', enable_default_from_environ=False)

    with pytest.raises(ValueError):
        a.add_argument('nope', enable_default_from_environ=True)

    with pytest.raises(ValueError):
        a.add_argument('-n', enable_default_from_environ=True)

    a.add_argument('--yep', enable_default_from_environ=True)

    with pytest.raises(RuntimeError):
        a.add_argument('--yep', enable_default_from_environ=True)
