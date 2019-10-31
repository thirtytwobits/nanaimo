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
import pathlib
import typing

import pytest

import nanaimo
import nanaimo.fixtures
import nanaimo.pytest_plugin


class Fixture(nanaimo.fixtures.SubprocessFixture):
    """
    This fixture assumes that scp is available and functional on the system.
    """

    fixture_name = 'nanaimo_scp'
    argument_prefix = 'scp'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--scp-file', help='The file to upload.')
        arguments.add_argument('--scp-remote-dir', help='The directory to upload to.')
        arguments.add_argument('--scp-target',
                               help='The IP or hostname for the target system.')
        arguments.add_argument('--scp-as-user',
                               help='The user to upload as.')

    def on_construct_command(cls, args: nanaimo.Namespace) -> str:
        """
        Form the upload command.
        """
        remote_directory = pathlib.Path(args.scp_remote_dir)
        remote_path = remote_directory / pathlib.Path(args.scp_file).stem
        cmd = 'scp {}{} {}@{}:{}'.format('-P {}'.format(args.scp_port) if args.scp_port is not None else '',
                                         str(args.scp_file), args.scp_as_user, args.scp_target, str(remote_path))
        return cmd


@nanaimo.fixtures.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_scp(request: typing.Any) -> nanaimo.fixtures.Fixture:
    return nanaimo.pytest_plugin.create_pytest_fixture(request, Fixture)
