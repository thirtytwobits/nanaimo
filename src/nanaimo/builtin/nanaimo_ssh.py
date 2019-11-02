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
import typing

import pytest

import nanaimo
import nanaimo.fixtures
import nanaimo.pytest.plugin


class Fixture(nanaimo.fixtures.SubprocessFixture):
    """
    This fixture assumes that ssh is available and functional on the system.
    """

    fixture_name = 'nanaimo_ssh'
    argument_prefix = 'ssh'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--ssh-target',
                               help='The IP or hostname for the target system.')
        arguments.add_argument('--ssh-as-user',
                               help='The user to upload as.')
        arguments.add_argument('--ssh-command',
                               help='The command to run.')
        arguments.add_argument('--ssh-identity',
                               help='The identify file to use')

    def on_construct_command(self, args: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        cmd = 'ssh {port} {ident} {user}@{target} \'{command}\''.format(
            port='-P {}'.format(args.ssh_port) if args.ssh_port is not None else '',
            command=str(args.ssh_command),
            user=args.ssh_as_user,
            target=args.ssh_target,
            ident='-i {}'.format(args.ssh_identity) if args.ssh_identity is not None else ''
        )
        return cmd


@nanaimo.fixtures.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_ssh(request: typing.Any) -> nanaimo.fixtures.Fixture:
    """
    The SSH fixture allows a test to run arbitrary commands on a remote device.
    This `pytest fixture <https://docs.pytest.org/en/latest/fixture.html>`_ provides
    a :class:`nanaimo.builtin.nanaimo_ssh.Fixture` fixture to a pytest.

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :rtype: nanaimo.builtin.nanaimo_ssh.Fixture
    """
    return nanaimo.pytest.plugin.create_pytest_fixture(request, Fixture.get_canonical_name())
