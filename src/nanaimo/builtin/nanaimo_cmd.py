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
        arguments.add_argument('--shell', '-C', help='A shell command to run as a subprocess.')

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
        return str(self.get_arg_covariant_or_fail(arguments, 'shell'))


def pytest_nanaimo_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
    return Fixture
