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
    Fixture that accepts a string argument ``cmd`` and executes it as a subprocess.

    .. invisible-code-block: python

        from nanaimo.fixtures import FixtureManager
        from nanaimo import Namespace, Arguments, Artifacts
        from nanaimo.builtin import nanaimo_cmd

        import os
        import asyncio

        loop = asyncio.get_event_loop()
        manager = FixtureManager(loop=loop)

    .. code-block:: python

        async def list_directory() -> Artifacts:

            cmd = nanaimo_cmd.Fixture(manager)

            return await cmd.gather(
                cmd_shell = ('dir' if os.name == 'nt' else 'ls -la')
            )

    .. invisible-code-block: python

        results = loop.run_until_complete(list_directory())

        assert 0 == results.result_code

    """

    fixture_name = 'nanaimo_cmd'
    argument_prefix = 'cmd'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        super().on_visit_test_arguments(arguments)
        arguments.add_argument('--cmd-shell', '-C', help='A shell command to run as a subprocess.')

    # +-----------------------------------------------------------------------+
    # | SubprocessFixture
    # +-----------------------------------------------------------------------+
    def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        """
        Called by the subprocess fixture to ask the specialization to form a command
        given a set of arguments.

        :param arguments: The arguments passed into :meth:`Fixture.on_gather`.
        :type arguments: nanaimo.Arguments
        :param inout_artifacts: A set of artifacts the superclass is assembling This
            is provided to the subclass to allow it to optionally contribute artifacts.
        :type inout_artifacts: nanaimo.Artifacts
        :return: The command to run in a subprocess shell.
        """
        optional_command = arguments.cmd_shell

        if isinstance(optional_command, str):
            return optional_command
        else:
            raise ValueError('No command provided (--cmd-shell, -C)')


@nanaimo.fixtures.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_cmd(request: typing.Any) -> nanaimo.fixtures.Fixture:
    """
    Provides a :class:`nanaimo.builtin.nanaimo_cmd.Fixture` fixture to a pytest.

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :rtype: nanaimo.builtin.nanaimo_cmd.Fixture
    """
    return nanaimo.pytest.plugin.create_pytest_fixture(request, Fixture.get_canonical_name())
