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
test fixture with the Nanaimo fixture manager use the `nanaimo.fixtures.PluggyFixtureManager.type_factory`
:class:`pluggy.HookimplMarker` to register your :class:`nanaimo.fixtures.Fixture`.

.. invisible-code-block: python
    import nanaimo
    import nanaimo.fixtures
    import pytest
    import typing

.. code-block:: python

    # In my_namespace/__init__.py

    class MyTestFixture(nanaimo.fixtures.Fixture):

        @classmethod
        def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
            pass

        async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
            artifacts = nanaimo.Artifacts()
            # Do your on-target testing here and store results in nanaimo.Artifacts.
            return artifacts


    @nanaimo.fixtures.PluggyFixtureManager.type_factory
    def get_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
        return MyTestFixture

Individual fixtures can choose to present pytest fixtures directly using `pytest.fixture`
and :func:`create_pytest_fixture`

.. code-block:: python

    @pytest.fixture
    def my_test_fixture(request: typing.Any) -> nanaimo.fixtures.Fixture:
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
import logging
import typing

import pytest

import nanaimo
import nanaimo.config
import nanaimo.fixtures

_fixture_manager = None  # type: typing.Optional[nanaimo.fixtures.FixtureManager]
"""
Pytest plugin singleton. The first time our pytest plugin is invoked
we populate to provide a peristent store of Nanaimo fixtures and artifacts.
"""


def _get_default_fixture_manager() -> nanaimo.fixtures.FixtureManager:
    global _fixture_manager
    if _fixture_manager is None:
        _fixture_manager = nanaimo.fixtures.nanaimo.fixtures.PluggyFixtureManager()
    return _fixture_manager


def create_pytest_fixture(pytest_request: typing.Any,
                          fixture_type: typing.Type[nanaimo.fixtures.Fixture]) -> nanaimo.fixtures.Fixture:
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
    args_ns = nanaimo.Namespace(args, nanaimo.config.ArgumentDefaults(args), allow_none_values=False)
    return fm.create_fixture(fixture_type.get_canonical_name(), args_ns)


def pytest_addoption(parser) -> None:  # type: ignore
    manager = _get_default_fixture_manager()
    nanaimo_defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()
    for fixture_type in manager.fixture_types():
        group = parser.getgroup(fixture_type.get_canonical_name())
        fixture_type.on_visit_test_arguments(nanaimo.Arguments(group,
                                                               nanaimo_defaults,
                                                               fixture_type.get_argument_prefix()))


@pytest.fixture
def nanaimo_fixture_manager(request: typing.Any) -> nanaimo.fixtures.FixtureManager:
    """
    The default fixture for Nanaimo. Available as `nanaimo_fixture_manager`

    .. invisible-code-block: python

        import nanaimo
        import nanaimo.fixtures
        import pytest
        import asyncio

    .. code-block:: python

        class MyFixture(nanaimo.fixtures.Fixture):

            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                pass

            async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                return nanaimo.Artifacts()

        def test_example(nanaimo_fixture_manager: nanaimo.fixtures.FixtureManager) -> None:

            with pytest.raises(KeyError):
                # If the fixture hasn't been registered with the manager
                # this throws.
                my_fixture = nanaimo_fixture_manager.create_fixture('my_fixture')

            # Use this when creating new fixtures.
            my_new_fixture = MyFixture(nanaimo_fixture_manager)

    .. invisible-code-block: python

        class DummyFixtureManager(nanaimo.fixtures.FixtureManager):
            def create_fixture(self,
                       fixture_name,
                       args = None,
                       loop = None):
                raise KeyError()

        test_example(DummyFixtureManager())

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :return: A reference to the default fixture manager.
    :rtype: nanaimo.fixtures.FixtureManager
    """
    return _get_default_fixture_manager()


@pytest.fixture
def nanaimo_arguments(request: typing.Any) -> nanaimo.Namespace:
    """
    Exposes the commandline arguments and defaults provided to a test.

    .. invisible-code-block: python

        import nanaimo
        import nanaimo.fixtures

    .. code-block:: python

        def test_example(nanaimo_arguments: nanaimo.Namespace) -> None:
            an_argument = nanaimo_arguments.some_arg

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :return: A namespace with the pytest commandline args added per the documented rules.
    :rtype: nanaimo.Namespace
    """
    return nanaimo.Namespace(request.config.option)


@pytest.fixture
def nanaimo_log(request: typing.Any) -> logging.Logger:
    """
    Provides the unit tests with a logger configured for use with the Nanaimo
    framework.

    .. note ::

        For now this is just a Python logger. Future revisions may add capabilities like the
        ability to log to a display or otherwise provide feedback to humans about the status
        of a test.

    .. invisible-code-block: python

        import nanaimo
        import logging

    .. code-block:: python

        def test_example(nanaimo_log: logging.Logger) -> None:
            nanaimo_log.info('Hiya')

    It's recommended that all Nanaimo tests configure logging in a tox.ini, pytest.ini, or
    pyproject.toml (when this is supported). For example, the following section in tox.ini
    would enable cli logging for nanaimo tests::

        [pytest]
        log_cli = true
        log_cli_level = DEBUG
        log_format = %(asctime)s %(levelname)s %(name)s: %(message)s
        log_date_format = %Y-%m-%d %H:%M:%S

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :return: A logger for use by Nanaimo tests.
    :rtype: logging.Logger
    """
    return logging.getLogger(request.function.__name__)
