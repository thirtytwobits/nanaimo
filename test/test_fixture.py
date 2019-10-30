#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import asyncio
import typing
from unittest.mock import patch

import pytest

import nanaimo


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


@pytest.mark.timeout(20)
@pytest.mark.asyncio
async def test_gather_timeout(gather_timeout_fixture: nanaimo.Fixture) -> None:
    """
    Test the standard fixture timeout.
    """
    gather_timeout_fixture.gather_timeout_seconds = 1.0
    with pytest.raises(asyncio.TimeoutError):
        await gather_timeout_fixture.gather()
