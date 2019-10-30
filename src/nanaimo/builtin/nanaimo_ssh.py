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
import asyncio
import typing

import pytest

import nanaimo
import nanaimo.pytest_plugin


class Fixture(nanaimo.Fixture):
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

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Do the upload. Return a status artifact.
        """
        artifacts = nanaimo.Artifacts()
        artifacts.result_code = await self._do_command(args.ssh_target, args.ssh_as_user, args.ssh_command)
        return artifacts

    async def _do_command(self,
                          target: str,
                          user: str,
                          command: str,
                          port: typing.Optional[int] = None) -> int:
        cmd = 'ssh {port} {user}@{target} \'{command}\''.format(
            port='-P {}'.format(port) if port is not None else '',
            command=str(command),
            user=user,
            target=target
        )

        self._logger.info(cmd)
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )  # type: asyncio.subprocess.Process

        stdout, stderr = await proc.communicate()

        self._logger.info('%s exited with %i', cmd, proc.returncode)

        if stdout:
            self._logger.debug(stdout.decode())
        if stderr:
            self._logger.error(stderr.decode())

        return proc.returncode


@nanaimo.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_ssh(request: typing.Any) -> nanaimo.Fixture:
    return nanaimo.pytest_plugin.create_pytest_fixture(request, Fixture)
