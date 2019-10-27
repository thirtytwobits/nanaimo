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
Nanaimo presents itself as a single pytest fixture called `nanaimo_fixture_manager`
which allows tests to access or control test hardware fixtures. To register your
test fixture with the Nanaimo fixture manager use the `nanaimo.PluggyFixtureManager.type_factory`
:class:`pluggy.HookimplMarker` to register your :class:`nanaimo.Fixture`.

.. invisible-code-block: python
    import nanaimo
    import pytest
    import typing

.. code-block:: python

    # In my_namespace/__init__.py

    class MyTestFixture(nanaimo.Fixture):

        @classmethod
        def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
            pass

        async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
            artifacts = nanaimo.Artifacts()
            # Do your on-target testing here and store results in nanaimo.Artifacts.
            return artifacts


    @nanaimo.PluggyFixtureManager.type_factory
    def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
        return MyTestFixture

Individual fixtures can choose to present pytest fixtures directly using `pytest.fixture`
and :func:`create_pytest_fixture`

.. code-block:: python

    @pytest.fixture
    def my_test_fixture(request: typing.Any) -> nanaimo.Fixture:
        return nanaimo.pytest_plugin.create_pytest_fixture(request, MyTestFixture)


In your setup.cfg you'll first need to register nanaimo with pytest ::

    [options]
        pytest11 =
            pytest_nanaimo = nanaimo.pytest_plugin

then, if you do want to expose your fixture directly, you'll need to add your fixture's namespace::

    [options]
        pytest11 =
            pytest_nanaimo = nanaimo.pytest_plugin
            pytest_my_plugin = my_namspace

"""
import typing

import pytest

import nanaimo

from .config import ArgumentDefaults

_fixture_manager = None  # type: typing.Optional[nanaimo.FixtureManager]
"""
Pytest plugin singleton. The first time our pytest plugin is invoked
we populate to provide a peristent store of Nanaimo fixtures and artifacts.
"""


def _get_default_fixture_manager() -> nanaimo.FixtureManager:
    global _fixture_manager
    if _fixture_manager is None:
        _fixture_manager = nanaimo.PluggyFixtureManager()
    return _fixture_manager


def create_pytest_fixture(pytest_request: typing.Any, fixture_type: typing.Type[nanaimo.Fixture]) -> nanaimo.Fixture:
    """
    Create a fixture for a `pytest.fixture` request. This method ensures the fixture is created through
    the default :class:`FixtureManager`.

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :return: Either a new fixture or a fixture of the same name that was already created for the default
        :class:`FixtureManager`.
    """
    fm = _get_default_fixture_manager()
    args = pytest_request.config.option
    args_ns = nanaimo.Namespace(args, ArgumentDefaults(args))
    return fm.create_fixture(fixture_type.get_canonical_name(), args_ns)


def pytest_addoption(parser) -> None:  # type: ignore
    manager = _get_default_fixture_manager()
    nanaimo_defaults = nanaimo.config.ArgumentDefaults()
    for fixture_type in manager.fixture_types():
        group = parser.getgroup(fixture_type.get_canonical_name())
        fixture_type.on_visit_test_arguments(nanaimo.Arguments(group, nanaimo_defaults))


@pytest.fixture
def nanaimo_fixture_manager(request: typing.Any) -> nanaimo.FixtureManager:
    """
    The default fixture for Nanaimo. Available as `nanaimo_fixture_manager`

    .. code-block:: python

        def test_example(nanaimo_fixture_manager: nanaimo.FixtureManager) -> None:
            my_fixture = nanaimo_fixture_manager.get_fixture('my_fixture')

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :return: A reference to the default fixture manager.
    """
    return _get_default_fixture_manager()
