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

import nanaimo


class Fixture(nanaimo.Fixture):
    """
    This fixture takes a list of other fixtures and runs them concurrently returning a
    :meth:`nanaimo.Artifacts.combine`ed set of :class:`nanaimo.Artifacts`.

    You can use this fixture directly in your unit tests:

    .. invisible-code-block: python

        from nanaimo import Namespace, FixtureManager, Arguments
        from nanaimo.builtin import nanaimo_bar, gather
        import asyncio
        import argparse

        loop = asyncio.get_event_loop()
        manager = FixtureManager(loop=loop)

    .. code-block:: python

        async def example1():

            bar_one = nanaimo_bar.Fixture(manager)
            bar_two = nanaimo_bar.Fixture(manager)
            gather_fixture = gather.Fixture(manager)

            return await gather_fixture.gather(
                gather_coroutine=[
                    bar_one.gather(bar_number=1),
                    bar_two.gather(bar_number=2)
                ]
            )

    .. invisible-code-block: python

        result = loop.run_until_complete(example1())

        assert 'bar_1' in result
        assert 'bar_2' in result

    You can also use the --gather-coroutines argument to specify fixtures by name::

        nait gather --gather-coroutine nanaimo_bar --gather-coroutine bkprecision --BC 1

    """

    fixture_name = 'nanaimo_gather'
    argument_prefix = 'gather'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--gather-coroutine', action='append')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Multi-plex fixture
        """
        fixture_list = []  # type: typing.List[typing.Coroutine]
        for arg in args.gather_coroutine:
            if asyncio.iscoroutine(arg):
                fixture_list.append(arg)
            else:
                fixture_list.append(self.manager.create_fixture(arg, args).gather())
        results = await asyncio.gather(*fixture_list, loop=self.loop)
        return nanaimo.Artifacts.combine(*results)


@nanaimo.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Fixture
