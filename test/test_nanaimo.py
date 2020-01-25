#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import argparse
import os
import typing
from unittest.mock import MagicMock

import pytest

import material
import nanaimo
import nanaimo.config
import nanaimo.connections
import nanaimo.connections.uart
import nanaimo.instruments.jlink
import nanaimo.parsers
import nanaimo.parsers.gtest
from nanaimo import set_subprocess_environment


@pytest.mark.timeout(10)
def test_uart_monitor(serial_simulator_type: typing.Type) -> None:
    """
    Verify the nanaimo.ConcurrentUart class using a mock serial port.
    """
    serial = serial_simulator_type(material.FAKE_TEST_SUCCESS)
    last_line = material.FAKE_TEST_SUCCESS[-1]
    with nanaimo.connections.uart.ConcurrentUart(serial) as monitor:
        while True:
            line = monitor.readline()
            if line is None:
                os.sched_yield()
                continue
            elif line == last_line:
                break


@pytest.mark.asyncio
async def test_failed_test(serial_simulator_type: typing.Type) -> None:
    serial = serial_simulator_type(material.FAKE_TEST_FAILURE)
    with nanaimo.connections.uart.ConcurrentUart(serial) as monitor:
        assert 1 == await nanaimo.parsers.gtest.Parser(10).read_test(monitor)


@pytest.mark.asyncio
async def test_timeout_while_monitoring(serial_simulator_type: typing.Type) -> None:
    serial = serial_simulator_type(['gibberish'], loop_fake_data=False)
    with nanaimo.connections.uart.ConcurrentUart(serial) as monitor:
        assert 0 != await nanaimo.parsers.gtest.Parser(4.0).read_test(monitor)


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


@pytest.mark.parametrize('required_prefix,test_positional_args,test_expected_args',
                         [  # type: ignore
                             ('tt', ['--foo-bar'], ['--tt-foo-bar']),
                             ('z', ['-f', '--foo-bar'], ['-f', '--z-foo-bar']),
                             ('pre', ['--foo-bar', '-x'], ['--pre-foo-bar', '-x']),
                             ('a', ['-foo-bar', '-x'], ['-foo-bar', '-x'])
                         ])
def test_require_prefix(required_prefix, test_positional_args, test_expected_args) -> None:
    parser = MagicMock(spec=argparse.ArgumentParser)
    parser.add_argument = MagicMock()

    a = nanaimo.Arguments(parser, required_prefix=required_prefix)

    a.add_argument(*test_positional_args)

    parser.add_argument.assert_called_once_with(*test_expected_args)


def test_set_subprocess_environment_no_environ() -> None:
    """
    Verify that no exceptions are thrown if the defaults config lacks an ``environ`` key.
    """
    defaults = MagicMock(spec=nanaimo.config.ArgumentDefaults)
    defaults.__getitem__ = MagicMock(side_effect=KeyError())

    set_subprocess_environment(nanaimo.Namespace(defaults=defaults))


def test_get_as_merged_dict() -> None:
    """
    Verify that no exceptions are thrown if the defaults config lacks an ``environ`` key
    when using Namespace.get_as_merged_dict()
    """
    defaults = MagicMock(spec=nanaimo.config.ArgumentDefaults)
    defaults.__getitem__ = MagicMock(side_effect=KeyError())

    nanaimo.Namespace(defaults=defaults).get_as_merged_dict('environ')
