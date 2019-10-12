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
import functools
import typing

import pytest

import nanaimo
import nanaimo.pytest_plugin


class Fixture(nanaimo.Fixture):
    """
    A trivial plugin. Returns an callable artifact named "eat" that logs a yummy info message when invoked.
    """

    fixture_name = 'nanaimo_bar'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        pass

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Create a delicious function in the artifacts to eat.
        """
        artifacts = nanaimo.Artifacts()
        self.logger.info("don't forget to eat your dessert.")
        setattr(artifacts, 'eat', functools.partial(self.logger.info, 'Nanaimo bars are yummy.'))
        return artifacts


@nanaimo.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Fixture


@pytest.fixture
def nanaimo_bar(request: typing.Any) -> nanaimo.Fixture:
    return nanaimo.pytest_plugin.create_pytest_fixture(request, Fixture)
