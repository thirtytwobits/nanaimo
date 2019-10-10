#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import asyncio
import contextlib
import pathlib
import typing
import nanaimo
import pytest
import argparse

import fixtures
import fixtures.simulators
from nanaimo.instruments.bkprecision import Series1900BUart
from nanaimo.connections.uart import ConcurrentUart
from unittest.mock import patch


@pytest.fixture
def paths_for_test():  # type: ignore
    return fixtures.Paths(__file__)


def create_dummy_serial_port_factory(fake_lines: typing.List[str],
                                     event_loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                                     loop_fake_data: bool = False) \
        -> Series1900BUart.UartFactoryType:

    @contextlib.contextmanager
    def dummy_serial_port(port: typing.Union[str, pathlib.Path]) -> typing.Generator:
        nonlocal fake_lines, event_loop
        with ConcurrentUart(fixtures.simulators.Serial(fake_lines, '\r'), event_loop, '\r', loop_fake_data) as bk_uart:
            print('Yielding context with a simulated serial port set to emit {} line(s) of fake output.'.format(len(fake_lines)))
            yield bk_uart

    return dummy_serial_port


def to_namespace(fixture_type: typing.Type[nanaimo.Fixture], command: str) -> nanaimo.Namespace:
    parser = argparse.ArgumentParser()
    fixture_type.on_visit_test_arguments(nanaimo.Arguments(parser))
    return nanaimo.Namespace(parser.parse_args(args=['--bk-port', 'dummy_port', '--bk-command', command]))


@pytest.mark.asyncio
@patch('nanaimo.FixtureManager')
async def test_turn_off(MockFixtureManager: typing.Any, paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    bk = Series1900BUart(nanaimo.FixtureManager(), event_loop, uart_factory=create_dummy_serial_port_factory(['OK'], event_loop))
    args = to_namespace(Series1900BUart, '0')
    assert 0 == int(await bk.gather(args))


@pytest.mark.asyncio
async def test_turn_on(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    bk = Series1900BUart(nanaimo.FixtureManager(), event_loop, uart_factory=create_dummy_serial_port_factory(['OK'], event_loop))
    args = to_namespace(Series1900BUart, '1')
    assert 0 == int(await bk.gather(args))


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_turn_on_timeout(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    bk = Series1900BUart(nanaimo.FixtureManager(), event_loop, uart_factory=create_dummy_serial_port_factory(['NOPE'], event_loop, loop_fake_data=False))
    with pytest.raises(asyncio.TimeoutError):
        await bk.gather(to_namespace(Series1900BUart, '1'))


@pytest.mark.asyncio
async def test_get_display(paths_for_test: fixtures.Paths, event_loop: asyncio.AbstractEventLoop) -> None:
    bk = Series1900BUart(nanaimo.FixtureManager(), event_loop, uart_factory=create_dummy_serial_port_factory(['030201451', 'OK'], event_loop))
    args = to_namespace(Series1900BUart, '?')
    artifacts = await bk.gather(args)
    display = artifacts.display
    assert 3.02 == display[0]
    assert 1.45 == display[1]
    assert Series1900BUart.StatusCC == display[2]
