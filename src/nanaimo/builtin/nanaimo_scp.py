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
        arguments.add_argument('--file', help='The file to upload.')
        arguments.add_argument('--remote-dir', help='The directory to upload to.')
        arguments.add_argument('--target',
                               help='The IP or hostname for the target system.')
        arguments.add_argument('--as-user',
                               help='The user to upload as.')
        arguments.add_argument('--identity',
                               help='The identify file to use')

    def on_construct_command(cls, args: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        """
        Form the upload command.
        """
        scp_file = cls.get_arg_covariant_or_fail(args, 'file')
        scp_port = cls.get_arg_covariant(args, 'port')
        scp_identity = cls.get_arg_covariant(args, 'identity')
        scp_as_user = cls.get_arg_covariant(args, 'as_user')
        scp_target = cls.get_arg_covariant_or_fail(args, 'target')

        remote_directory = pathlib.Path(cls.get_arg_covariant_or_fail(args, 'remote_dir'))
        remote_path = remote_directory / pathlib.Path(scp_file).name
        port_string = '-P {}'.format(scp_port) if scp_port is not None else ''
        identity_string = '-i {}'.format(scp_identity) if scp_identity is not None else ''
        scp_as_user_string = ('{}@'.format(scp_as_user) if scp_as_user is not None else scp_as_user)

        setattr(inout_artifacts, 'remote_path', remote_path)

        cmd = 'scp {ident} {port}{file} {user}{target}:{remote_path}'.format(port=port_string,
                                                                             file=str(scp_file),
                                                                             user=scp_as_user_string,
                                                                             target=scp_target,
                                                                             remote_path=str(remote_path),
                                                                             ident=identity_string)
        return cmd


def pytest_nanaimo_fixture_type() -> typing.Type['Fixture']:
    return Fixture
