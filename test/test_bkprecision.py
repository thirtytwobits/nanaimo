#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import asyncio

import pytest

import fixtures
import fixtures.simulators
from nanaimo.connections.uart import ConcurrentUart
from nanaimo.instruments.bkprecision import Series1900BUart


@pytest.fixture
def paths_for_test():  # type: ignore
    return fixtures.Paths(__file__)


@pytest.mark.asyncio
async def test_turn_off(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    fake_serial = fixtures.simulators.Serial(['OK'], '\r')
    with ConcurrentUart(fake_serial, eol='\r') as serial_sim:
        bk = Series1900BUart(serial_sim)
        await bk.turn_off()


@pytest.mark.asyncio
async def test_turn_on(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    fake_serial = fixtures.simulators.Serial(['OK'], '\r')
    with ConcurrentUart(fake_serial, eol='\r') as serial_sim:
        bk = Series1900BUart(serial_sim)
        await bk.turn_on()


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_turn_on_timeout(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    fake_serial = fixtures.simulators.Serial(['NOPE'], '\r', loop_fake_data=False)
    with ConcurrentUart(fake_serial, eol='\r') as serial_sim:
        bk = Series1900BUart(serial_sim, 1)
        with pytest.raises(asyncio.TimeoutError):
            await bk.turn_on()


@pytest.mark.asyncio
async def test_get_display(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    fake_serial = fixtures.simulators.Serial(['030201451', 'OK'], '\r', loop_fake_data=True)
    with ConcurrentUart(fake_serial, eol='\r') as serial_sim:
        bk = Series1900BUart(serial_sim)
        display = await bk.get_display()
        assert 3.02 == display[0]
        assert 1.45 == display[1]
        assert Series1900BUart.StatusCC == display[2]
