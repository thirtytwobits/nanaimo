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
        super().on_visit_test_arguments(arguments)
        arguments.add_argument('--target',
                               help='The IP or hostname for the target system.')
        arguments.add_argument('--as-user',
                               help='The user to upload as.')
        arguments.add_argument('--command',
                               help='The command to run.')
        arguments.add_argument('--identity',
                               help='The identify file to use')

    def on_construct_command(self, args: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        ssh_command = self.get_arg_covariant_or_fail(args, 'command')
        ssh_port = self.get_arg_covariant(args, 'port')
        ssh_as_user = self.get_arg_covariant(args, 'as_user')
        ssh_target = self.get_arg_covariant_or_fail(args, 'target')
        ssh_identity = self.get_arg_covariant(args, 'identity')

        cmd = 'ssh {port} {ident} {user}{target} \'{command}\''.format(
            port='-P {}'.format(ssh_port) if ssh_port is not None else '',
            command=str(ssh_command),
            user=('{}@'.format(ssh_as_user) if ssh_as_user is not None else ''),
            target=ssh_target,
            ident='-i {}'.format(ssh_identity) if ssh_identity is not None else ''
        )
        return cmd


def pytest_nanaimo_fixture_type() -> typing.Type['Fixture']:
    return Fixture
