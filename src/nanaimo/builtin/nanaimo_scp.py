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
import pathlib
import typing

import pytest

import nanaimo
import nanaimo.pytest_plugin


class Fixture(nanaimo.Fixture):
    """
    This fixture assumes that scp is available and functional on the system.
    """

    fixture_name = 'nanaimo_scp'
    argument_prefix = 'scp'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--scp-file', help='The file to upload.')
        arguments.add_argument('--scp-remote-dir', help='The file to upload.')
        arguments.add_argument('--scp-target',
                               help='The IP or hostname for the target system.')
        arguments.add_argument('--scp-as-user',
                               help='The user to upload as.')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Do the upload. Return a status artifact.
        """
        artifacts = nanaimo.Artifacts()
        remote_directory = pathlib.Path(args.scp_remote_dir)
        artifacts.result_code = await self._upload(args.scp_file, remote_directory, args.scp_target, args.scp_as_user)
        setattr(artifacts, 'remote_path', remote_directory / pathlib.Path(args.scp_file).stem)
        return artifacts

    async def _upload(self,
                      file_to_upload: pathlib.Path,
                      target_path: pathlib.Path,
                      target: str,
                      user: str,
                      port: typing.Optional[int] = None) -> int:
        cmd = 'scp {}{} {}@{}:{}'.format('-P {}'.format(port) if port is not None else '',
                                         str(file_to_upload), user, target, str(target_path))

        self._logger.info('starting upload: %s', cmd)
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
def nanaimo_scp(request: typing.Any) -> nanaimo.Fixture:
    return nanaimo.pytest_plugin.create_pytest_fixture(request, Fixture)
