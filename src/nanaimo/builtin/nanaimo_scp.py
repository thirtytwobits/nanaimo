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
import nanaimo.pytest.plugin


class Fixture(nanaimo.fixtures.SubprocessFixture):
    """
    This fixture assumes that scp is available and functional on the system.
    """

    fixture_name = 'nanaimo_scp'
    argument_prefix = 'scp'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        super().on_visit_test_arguments(arguments)
        arguments.add_argument('--scp-file', help='The file to upload.')
        arguments.add_argument('--scp-remote-dir', help='The directory to upload to.')
        arguments.add_argument('--scp-target',
                               help='The IP or hostname for the target system.')
        arguments.add_argument('--scp-as-user',
                               help='The user to upload as.')
        arguments.add_argument('--scp-identity',
                               help='The identify file to use')

    def on_construct_command(cls, args: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        """
        Form the upload command.
        """
        remote_directory = pathlib.Path(args.scp_remote_dir)
        remote_path = remote_directory / pathlib.Path(args.scp_file).name
        port_string = '-P {}'.format(args.scp_port) if args.scp_port is not None else ''
        identity_string = '-i {}'.format(args.scp_identity) if args.scp_identity is not None else ''

        setattr(inout_artifacts, 'remote_path', remote_path)

        cmd = 'scp {ident} {port}{file} {user}@{target}:{remote_path}'.format(port=port_string,
                                                                              file=str(args.scp_file),
                                                                              user=args.scp_as_user,
                                                                              target=args.scp_target,
                                                                              remote_path=str(remote_path),
                                                                              ident=identity_string)
        return cmd


@nanaimo.fixtures.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_scp(request: typing.Any) -> nanaimo.fixtures.Fixture:
    """
    The SCP fixture allows a test to use SSH to copy files to a target system.
    This `pytest fixture <https://docs.pytest.org/en/latest/fixture.html>`_ provides
    a :class:`nanaimo.builtin.nanaimo_scp.Fixture` fixture to a pytest.

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :rtype: nanaimo.builtin.nanaimo_scp.Fixture
    """
    return nanaimo.pytest.plugin.create_pytest_fixture(request, Fixture.get_canonical_name())
