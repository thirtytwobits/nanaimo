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

import pytest

import nanaimo
import nanaimo.fixtures
import nanaimo.pytest.plugin


class Fixture(nanaimo.fixtures.SubprocessFixture):
    """
    Fixture for controlling Yepkit USB hubs with switchable power. For example
    the `YKUSH3 <https://www.yepkit.com/product/300110/YKUSH3>`_ is a 3-port
    USB-3 hub that allows individual control of the power rails for each port.
    """

    fixture_name = 'nanaimo_ykush'
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
                               help='Simple pass through of arguments to ')

    def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        serial_arg = self.get_arg_covariant(arguments, 'serial')
        serial = ('' if serial_arg is None else ' -s ' + serial_arg)
        return '{ykush_cmd} {board}{serial} {command}'.format(
            ykush_cmd=self.ykush_cmd,
            board=self.get_arg_covariant(arguments, 'model', ''),
            serial=serial,
            command=self.get_arg_covariant(arguments, 'command')
        )


@nanaimo.fixtures.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_instr_ykush(request: typing.Any) -> nanaimo.fixtures.Fixture:
    """
    Provides a :class:`nanaimo.instruments.ykush.Fixture` fixture to a pytest.
    This fixture controls a `YKUSH <https://www.yepkit.com/products/ykush>`_
    family board attached to the system via USB.

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :return: A fixture providing control of a YKUSH usb hub.
    :rtype: nanaimo.instruments.ykush.Fixture
    """
    return nanaimo.pytest.plugin.create_pytest_fixture(request, Fixture.get_canonical_name())
