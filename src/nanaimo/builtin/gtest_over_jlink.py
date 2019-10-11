#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
#                                       (@@@@%%%%%%%%%&@@&.
#                              /%&&%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%&@@(
#                              *@&%%%%%%%%%&&%%%%%%%%%%%%%%%%%%&&&%%%%%%%
#                               @   @@@(@@@@%%%%%%%%%%%%%%%%&@@&* @@@   .
#                               ,   .        .  .@@@&                   /
#                                .       .                              *
#                               @@              .                       @
#                              @&&&&&&@. .    .                     *@%&@
#                              &&&&&&&&&&&&&&&&@@        *@@############@
#                     *&/ @@ #&&&&&&&&&&&&&&&&&&&&@  ###################*
#                              @&&&&&&&&&&&&&&&&&&##################@
#                                 %@&&&&&&&&&&&&&&################@
#                                        @&&&&&&&&&&%#######&@%
#  nanaimo                                   (@&&&&####@@*
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
    """
    Uploads a firmware using JLink and monitors a UART expected gtest output. Returns 0 if all
    gtest tests pass else returns non-zero.
    """
    fixture_name = 'gtest_over_jlink'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        nanaimo.connections.uart.ConcurrentUart.on_visit_test_arguments(arguments)
        nanaimo.instruments.jlink.ProgramUploaderJLink.on_visit_test_arguments(arguments)
        arguments.add_argument('--gtest-timeout',
                               default=30.0,
                               type=float,
                               help='Time to wait for the gtest to complete in seconds.')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:

        uploader = nanaimo.instruments.jlink.ProgramUploaderJLink()
        jlink_scripts = pathlib.Path(args.base_path).glob(args.jlink_scripts)
        parser = nanaimo.parsers.gtest.Parser(args.gtest_timeout)

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


@nanaimo.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Fixture


@pytest.fixture
def gtest_over_jlink(request: typing.Any) -> nanaimo.Fixture:
    return nanaimo.pytest_plugin.create_pytest_fixture(request, Fixture)
