#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import typing

import pytest

import nanaimo
import nanaimo.builtin
import nanaimo.builtin.nanaimo_serial_watch
import nanaimo.connections
import nanaimo.connections.uart


@pytest.mark.asyncio
async def test_default_match(nanaimo_serial_watch: nanaimo.builtin.nanaimo_serial_watch.Fixture,
                             serial_simulator_type: typing.Type) -> None:
    """
    The default match matches everything in the first line.
    """
    simulated_serial = serial_simulator_type(['one', 'two'])

    def uart_factory(*args: typing.Any) -> nanaimo.connections.uart.ConcurrentUart:
        return nanaimo.connections.uart.ConcurrentUart(simulated_serial)
    nanaimo_serial_watch._uart_factory = uart_factory
    artifacts = await nanaimo_serial_watch.gather(lw_port='foo')
    assert artifacts.matched_line == 'one'


@pytest.mark.asyncio
async def test_realistic_match(nanaimo_serial_watch: nanaimo.builtin.nanaimo_serial_watch.Fixture,
                               serial_simulator_type: typing.Type) -> None:
    """
    Now test a more realistic matching scenario.
    """
    line_to_match = 'FOO LINUX Distribution 7.5'
    simulated_serial = serial_simulator_type([
        'UAVCAN is an open lightweight protocol designed for reliable',
        'communication in aerospace and robotic applications',
        'via robust vehicle bus networks.',

        line_to_match,

        'Features:',
        '- Democratic network – no bus master, no single point of',
        'failure.',
        '- Publish/subscribe and request/response (RPC1)',
        'exchange semantics.'
    ])

    def uart_factory(*args: typing.Any) -> nanaimo.connections.uart.ConcurrentUart:
        return nanaimo.connections.uart.ConcurrentUart(simulated_serial)
    nanaimo_serial_watch._uart_factory = uart_factory
    artifacts = await nanaimo_serial_watch.gather(lw_port='foo', lw_pattern=r'LINUX\s+Distribution\s+(\d+\.\d+)')
    assert artifacts.matched_line == line_to_match
    assert artifacts.match.group(1) == '7.5'
