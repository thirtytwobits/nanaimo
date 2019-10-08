#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
Built-in :class:`Fixture` objects for common scenarios. See individual fixture documentation for use.
"""
import asyncio
import pathlib
import typing

import pytest

import nanaimo
import nanaimo.connections
import nanaimo.connections.uart
import nanaimo.instruments
import nanaimo.instruments.jlink
import nanaimo.parsers
import nanaimo.parsers.gtest
import nanaimo.pytest_plugin


class Fixture(nanaimo.Fixture):

    fixture_name = 'gtest_over_jlink'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        nanaimo.connections.uart.ConcurrentUart.on_visit_test_arguments(arguments)
        nanaimo.instruments.jlink.ProgramUploaderJLink.on_visit_test_arguments(arguments)

    async def gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:

        uploader = nanaimo.instruments.jlink.ProgramUploaderJLink()
        jlink_scripts = pathlib.Path(args.base_path).glob(args.jlink_scripts)
        parser = nanaimo.parsers.gtest.Parser(args.test_timeout_seconds)

        result = 0
        with nanaimo.connections.uart.ConcurrentUart.new_default(args.port, args.port_speed) as monitor:
            for script in jlink_scripts:
                if result != 0:
                    break
                result = await asyncio.wait_for(uploader.upload(script), timeout=args.upload_timeout_seconds)
                if result != 0:
                    break
                result = await parser.read_test(monitor)

        return nanaimo.Artifacts(result)


@nanaimo.FixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Fixture


@pytest.fixture
def gtest_over_jlink(request: typing.Any) -> nanaimo.Fixture:
    return nanaimo.pytest_plugin.create_pytest_fixture(request, Fixture)
