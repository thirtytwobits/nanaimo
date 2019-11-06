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
Nanaimo provides a collection of pytest fixtures all defined in this module.

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
        return nanaimo.pytest.plugin.create_pytest_fixture(request, MyTestFixture.get_canonical_name())


In your setup.cfg you'll first need to register nanaimo with pytest ::

    [options]
        pytest11 =
            pytest_nanaimo = nanaimo.pytest.plugin

then, if you do want to expose your fixture directly, you'll need to add your fixture's namespace::

    [options]
        pytest11 =
            pytest_nanaimo = nanaimo.pytest.plugin
            pytest_my_plugin = my_namspace

"""
import logging
import typing

import _pytest
import pytest

import nanaimo
import nanaimo.config
import nanaimo.display
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
                          canonical_name: str) -> nanaimo.fixtures.Fixture:
    """
    Create a fixture for a `pytest.fixture` request. This method ensures the fixture is created through
    the default :class:`FixtureManager`. For example, using :class:`nanaimo.fixtures.PluggyFixtureManager`
    you must first register your fixture like thus::

        @nanaimo.fixtures.PluggyFixtureManager.type_factory
        def get_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
            return MyFixtureType

    Then you can register your fixture with pytest like this::

        @pytest.fixture
        def nanaimo_pytest_my_fixture(request: typing.Any) -> nanaimo.fixtures.Fixture:
            return nanaimo.pytest.plugin.create_pytest_fixture(request, MyFixtureType.canonical_name())

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :param canonical_name: The canonical name of the fixture to create
        (see :meth:`nanaimo.fixtures.Fixture.get_canonical_name`).
    :return: Either a new fixture or a fixture of the same name that was already created for the default
        :class:`FixtureManager`.
    :raises KeyError: if ``fixture_type`` was not a registered nanaimo fixture.
    """
    fm = _get_default_fixture_manager()
    args = pytest_request.config.option
    args_ns = nanaimo.Namespace(args, nanaimo.config.ArgumentDefaults(args), allow_none_values=False)
    return fm.create_fixture(canonical_name, args_ns)


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


def assert_success(artifacts: nanaimo.Artifacts) -> nanaimo.Artifacts:
    """
    Syntactic sugar to allow more fluent handling of :meth:`fixtures.Fixture.gather`
    artifacts. For example:

    .. invisible-code-block: python

        import asyncio
        import nanaimo
        from nanaimo import Artifacts
        from nanaimo.fixtures import Fixture, FixtureManager

        _doc_loop = asyncio.new_event_loop()

        class DummyFixture(Fixture):
            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                pass

            async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                return nanaimo.Artifacts()

        fixture = DummyFixture(FixtureManager(loop=_doc_loop))

    .. code-block:: python

        from nanaimo.pytest.plugin import assert_success

        async def test_my_fixture():

            artifacts = assert_success(await fixture.gather())

            # Now we can use the artifacts. If the gather had returned
            # non-zero for the result_code an assertion error would have
            # been raised.

    .. invisible-code-block: python

        _doc_loop.run_until_complete(test_my_fixture())

    :param artifacts: The artifacts to assert on.
    :type artifacts: nanaimo.Artifacts
    :returns: artifacts (for convenience).
    :rtype: nanaimo.Artifacts()
    """
    assert artifacts.result_code == 0
    return artifacts


def assert_success_if(artifacts: nanaimo.Artifacts,
                      conditional: typing.Callable[[nanaimo.Artifacts], bool]) -> nanaimo.Artifacts:
    """
    Syntactic sugar to allow more fluent handling of :meth:`fixtures.Fixture.gather`
    artifacts but with a user-supplied conditional.

    .. invisible-code-block: python

        import asyncio
        import pytest
        import nanaimo
        from nanaimo import Artifacts
        from nanaimo.fixtures import Fixture, FixtureManager

        _doc_loop = asyncio.new_event_loop()

        class DummyFixture(Fixture):
            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                pass

            async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                a = nanaimo.Artifacts()
                setattr(a, 'foo', 'bar')
                return a

        fixture = DummyFixture(FixtureManager(loop=_doc_loop))

    .. code-block:: python

        from nanaimo.pytest.plugin import assert_success_if

        async def test_my_fixture():

            def fail_if_no_foo(artifacts: Artifacts) -> bool:
                return 'foo' in artifacts

            artifacts = assert_success_if(await fixture.gather(), fail_if_no_foo)

            print('artifacts have foo. It\'s value is {}'.format(artifacts.foo))

    .. invisible-code-block: python

        _doc_loop.run_until_complete(test_my_fixture())

        async def test_failure():

            assert_success_if(await fixture.gather(), lambda _: False)

        with pytest.raises(AssertionError):
            _doc_loop.run_until_complete(test_failure())

    :param artifacts: The artifacts to assert on.
    :type artifacts: nanaimo.Artifacts
    :param conditiona: A method called to evaluate gathered artifacts iff :data:`Artifacts.result_code` is 0.
        Return False to trigger an assertion, True to pass.
    :returns: artifacts (for convenience).
    :rtype: nanaimo.Artifacts()
    """
    assert artifacts.result_code == 0
    assert conditional(artifacts)
    return artifacts


_display_singleton = None  # type: typing.Optional[nanaimo.display.CharacterDisplay]


def _get_display() -> nanaimo.display.CharacterDisplay:
    global _display_singleton
    if _display_singleton is None:
        # TODO: #65, use generic version
        _display_singleton = typing.cast(nanaimo.display.CharacterDisplay,
                                         _get_default_fixture_manager().create_fixture('character_display'))
    return _display_singleton


def pytest_sessionstart(session: _pytest.main.Session) -> None:
    _get_display().set_bg_colour(0, 0, 255)


def pytest_runtest_setup(item: typing.Any) -> None:
    display = _get_display()
    display.clear(display_default_message=False)
    display.write(item.name)


def pytest_sessionfinish(session: _pytest.main.Session, exitstatus: int) -> None:
    display = _get_display()
    display.clear(display_default_message=True)
    if exitstatus == 0:
        display.set_bg_colour(0, 255, 0)
    else:
        display.set_bg_colour(255, 0, 0)
