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
import time
import typing

import nanaimo
import nanaimo.fixtures
import nanaimo.pytest.plugin


class Fixture(nanaimo.fixtures.Fixture):
    """
    A trivial plugin. Returns an callable artifact named "eat" that logs a yummy info message when invoked.
    """

    fixture_name = 'nanaimo_bar'
    argument_prefix = 'nb'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        pass

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Create a delicious function in the artifacts to eat.

        +--------------+---------------------------+-----------------------------------------------+
        | **Returned Artifacts**                                                                   |
        +--------------+---------------------------+-----------------------------------------------+
        | key          | type                      | Notes                                         |
        +==============+===========================+===============================================+
        | eat          | Callable[[],None]         | A function that logs a message                |
        +--------------+---------------------------+-----------------------------------------------+
        | bar_{number} | str                       | A string formed from an argument              |
        |              |                           | ``bar_number``. This allows testing ordering  |
        |              |                           | of concurrent operations.                     |
        +--------------+---------------------------+-----------------------------------------------+
        """
        artifacts = nanaimo.Artifacts()
        self.logger.info("don't forget to eat your dessert.")
        setattr(artifacts, 'eat', functools.partial(self.logger.info, 'Nanaimo bars are yummy.'))
        setattr(artifacts, 'bar_{}'.format(args.bar_number), time.monotonic())
        return artifacts


def pytest_nanaimo_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
    return Fixture
