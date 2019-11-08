#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import argparse
import asyncio
import os
import pathlib
import typing
from unittest.mock import MagicMock

import pytest

import material
import nanaimo
import nanaimo.config
import nanaimo.connections
import nanaimo.connections.uart
import nanaimo.instruments.jlink
import nanaimo.parsers.gtest
from nanaimo.config import set_subprocess_environment_from_defaults


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
                                        s32K144_jlink_scripts: typing.Iterator[pathlib.Path],
                                        serial_simulator_type: typing.Type) -> None:
    scripts = s32K144_jlink_scripts
    uploader = nanaimo.instruments.jlink.ProgramUploaderJLink(mock_JLinkExe)
    serial = serial_simulator_type(material.FAKE_TEST_SUCCESS)
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
                # TODO: this can fail. Fruity test. Fixme
                assert 0 == result
            uploads += 1
    assert uploads > 1


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


def test_set_subprocess_environment_from_defaults_no_environ() -> None:
    """
    Verify that no exceptions are thrown if the defaults config lacks an ``environ`` key.
    """
    defaults = MagicMock(spec=nanaimo.config.ArgumentDefaults)
    defaults.__getitem__ = MagicMock(side_effect=KeyError())

    assert not set_subprocess_environment_from_defaults(defaults)
