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
TODO: See https://www.learn.yepkit.com/reference/ykushcmd-reference-ykush/1/2 for the command
strings.
"""

import typing

import nanaimo
import nanaimo.fixtures
import nanaimo.pytest.plugin


class Fixture(nanaimo.fixtures.SubprocessFixture):
    """
    Fixture for controlling Yepkit USB hubs with switchable power. For example
    the `YKUSH3 <https://www.yepkit.com/product/300110/YKUSH3>`_ is a 3-port
    USB-3 hub that allows individual control of the power rails for each port.

    This is a subprocess fixture that requires the ``ykushcmd`` program is available in the subprocess
    environment (see Yepkit's documentation for how to build this from source). All arguments can be
    overridden via the fixtures gather method. The supported commands are:

    +-----------------+--------------------------------------------------------+----------------------------+
    | command         | example                                                | Description                |
    +=================+========================================================+============================+
    | ``yku-all-on``  | ``await nanaimo_instr_ykush.gather(yku_all_on=True)``  | Turn on power to all ports |
    |                 |                                                        | on the YKUSH.              |
    +-----------------+--------------------------------------------------------+----------------------------+
    | ``yku-all-off`` | ``await nanaimo_instr_ykush.gather(yku_all_off=True)`` | Turn off power to all      |
    |                 |                                                        | ports on the YKUSH.        |
    +-----------------+--------------------------------------------------------+----------------------------+
    | ``yku-command`` | ``await nanaimo_instr_ykush.gather(yku_command='-l')`` | Pass-through any command   |
    |                 |                                                        | to ykushcmd.               |
    +-----------------+--------------------------------------------------------+----------------------------+
    """

    fixture_name = 'nanaimo_instr_ykush'
    argument_prefix = 'yku'

    ykush_cmd = 'ykushcmd'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--model',
                               default='ykush3',
                               help='The ykush board type.')
        arguments.add_argument('--serial',
                               help='A serial number of the board to send the command to.')
        arguments.add_argument('--command',
                               help='Simple pass through of arguments to {}'.format(cls.ykush_cmd))
        arguments.add_argument('--all-on',
                               action='store_true',
                               help='Turn on power to all ports (--{}-command will be ignored)'
                               .format(cls.argument_prefix))
        arguments.add_argument('--all-off',
                               action='store_true',
                               help='Turn on power to all ports (--{}-command will be ignored)'
                               .format(cls.argument_prefix))

    def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        """
        .. invisible-code-block: python

            from nanaimo.fixtures import FixtureManager
            from nanaimo import Namespace, Arguments, Artifacts
            from nanaimo.instruments import ykush

            import os
            import asyncio

            loop = asyncio.get_event_loop()
            manager = FixtureManager(loop=loop)

            cmd = ykush.Fixture(manager)

            ns = Namespace()
            artifacts = Artifacts()

            command = cmd.on_construct_command(ns, artifacts)
            assert command.find('-h') > 0

            setattr(ns, '{}_all_off'.format(ykush.Fixture.get_argument_prefix()), True)
            command = cmd.on_construct_command(ns, artifacts)
            assert command.find('-d a') > 0
            setattr(ns, '{}_all_off'.format(ykush.Fixture.get_argument_prefix()), None)

            setattr(ns, '{}_all_on'.format(ykush.Fixture.get_argument_prefix()), True)
            command = cmd.on_construct_command(ns, artifacts)
            assert command.find('-u a') > 0

            # off takes precedence
            setattr(ns, '{}_all_off'.format(ykush.Fixture.get_argument_prefix()), True)
            command = cmd.on_construct_command(ns, artifacts)
            assert command.find('-d a') > 0
            setattr(ns, '{}_all_off'.format(ykush.Fixture.get_argument_prefix()), None)
            setattr(ns, '{}_all_on'.format(ykush.Fixture.get_argument_prefix()), None)

            setattr(ns, '{}_command'.format(ykush.Fixture.get_argument_prefix()), 'foo')
            command = cmd.on_construct_command(ns, artifacts)
            assert command.find('foo') > 0

        """
        serial_arg = self.get_arg_covariant(arguments, 'serial')
        serial = ('' if serial_arg is None else ' -s ' + serial_arg)

        all_on = self.get_arg_covariant(arguments, 'all_on', False)
        all_off = self.get_arg_covariant(arguments, 'all_off', False)
        pass_thru = self.get_arg_covariant(arguments, 'command')

        if all_off:
            self._logger.debug('Turning all ports off.')
            command = '-d a'
        elif all_on:
            self._logger.debug('Turning all ports on.')
            command = '-u a'
        elif pass_thru is not None:
            command = str(pass_thru)
            self._logger.debug('Passing through command {}'.format(pass_thru))
        else:
            command = '-h'

        return '{ykush_cmd} {board}{serial} {command}'.format(
            ykush_cmd=self.ykush_cmd,
            board=self.get_arg_covariant(arguments, 'model', ''),
            serial=serial,
            command=command
        )


def pytest_nanaimo_fixture_type() -> typing.Type['Fixture']:
    return Fixture
