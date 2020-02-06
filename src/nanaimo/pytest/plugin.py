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

        fixture_name = 'my_fixture_name'
        argument_prefix = 'mfn'

        @classmethod
        def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
            pass

        async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
            artifacts = nanaimo.Artifacts()
            # Do your on-target testing here and store results in nanaimo.Artifacts.
            return artifacts


    def pytest_nanaimo_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
        '''
        This is required to provide the fixture to pytest as a fixture.
        '''
        return MyTestFixture


In your setup.cfg you'll first need to register nanaimo with pytest ::

    [options]
        pytest11 =
            pytest_nanaimo = nanaimo.pytest.plugin

then you'll need to add your fixture's namespace::

    [options]
        pytest11 =
            pytest_nanaimo = nanaimo.pytest.plugin
            pytest_nanaimo_plugin_my_fixture = my_namspace

.. note ::
    For Nanaimo the key for your plugin in the pytest11 map is unimportant. It must be unique but
    nothing else about it will be visible to your tests unless you integrate more deeply with pytest.
    The fixture you expose from your plugin via ``pytest_nanaimo_fixture_type`` will be
    named for the canonical name of your :class:`Fixture <nanaimo.fixtures.Fixture>` (in this case,
    "my_fixture_name").

You can add as many additional nanaimo plugins as you want but you can only have one
:class:`Fixture <nanaimo.fixtures.Fixture>` in each module.

Where you don't need your Nanaimo fixture to be redistributable you may also use standard
pytest fixture creation by using the :func:`nanaimo_fixture_manager <nanaimo.pytest.plugin.nanaimo_fixture_manager>`
and :func:`nanaimo_arguments <nanaimo.pytest.plugin.nanaimo_arguments>` fixtures supplied by
the core nanaimo pytest plugin. For example, assuming you have ``nanaimo.pytest.plugin`` in your setup.cfg
(see above) you can do something like this in a ``conftest.py`` ::

    @pytest.fixture
    def my_fixture_name(nanaimo_fixture_manager, nanaimo_arguments) -> 'nanaimo.fixtures.Fixture':
        '''
        It is considered a best-practice to always name your pytest.fixture method the
        same as your Fixture's canonical name (i.e. fixture_name).
        '''
        return MyTestFixture(nanaimo_fixture_manager, nanaimo_arguments)

"""
import asyncio
import logging
import re
import textwrap
import typing

import _pytest
import py
import pytest

import nanaimo
import nanaimo.config
import nanaimo.fixtures
import nanaimo.display


def create_pytest_fixture(request: typing.Any, fixture_name: str) -> 'nanaimo.fixtures.Fixture':
    """
    DEPRECATED. Use the appropriate :meth:`FixtureManager <nanaimo.fixtures.FixtureManager>`
    and its
    :meth:`FixtureManager.create_fixture <nanaimo.fixtures.FixtureManager.create_fixture>`
    method instead.
    """
    raise DeprecationWarning('This method has been removed. All fixtures must be created '
                             'using a FixtureManager instance in this version and going forward.')


# +---------------------------------------------------------------------------+
# | NANAIMO PYTEST FIXTURES
# |                  (not Nanaimo Fixture, fixtures. I know, just go with it)
# +---------------------------------------------------------------------------+


@pytest.fixture
def nanaimo_fixture_manager(request: typing.Any) \
        -> nanaimo.fixtures.FixtureManager:
    """
    Provides a default :class:`FixtureManager <nanaimo.fixtures.FixtureManager>` to a test.

    .. invisible-code-block: python

        import nanaimo
        import nanaimo.fixtures

    .. code-block:: python

        def test_example(nanaimo_fixture_manager: nanaimo.Namespace) -> None:
            common_loop = nanaimo_fixture_manager.loop

    :param pytest_request: The request object passed into the pytest fixture factory.
    :type pytest_request: _pytest.fixtures.FixtureRequest
    :return: A new fixture manager.
    :rtype: nanaimo.fixtures.FixtureManager
    """
    return PytestFixtureManager(request.config.pluginmanager)


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


# +---------------------------------------------------------------------------+
# | NANAIMO PYTEST HELPERS
# +---------------------------------------------------------------------------+

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

# +===========================================================================+
# | NANAIMO PYTEST PLUGIN INTERNALS
# +===========================================================================+


class PytestFixtureManager(nanaimo.fixtures.FixtureManager):
    """
    :class:`FixtureManager <nanaimo.fixtures.FixtureManager>` implemented using
    pytest plugin APIs.
    """

    def __init__(self,
                 pluginmanager: '_pytest.config.PytestPluginManager',
                 loop: typing.Optional[asyncio.AbstractEventLoop] = None):
        super().__init__(loop=loop)
        self._pluginmanager = pluginmanager

    def create_fixture(self,
                       canonical_name: str,
                       args: typing.Optional[nanaimo.Namespace] = None,
                       loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> nanaimo.fixtures.Fixture:
        fixture_plugin = self._pluginmanager.get_plugin(canonical_name)
        fixture_type = fixture_plugin.fixture_type
        return fixture_type(self, args)


# +---------------------------------------------------------------------------+
# | INTERNALS :: INTEGRATED DISPLAY
# +---------------------------------------------------------------------------+

_display_singleton = None  # type: typing.Optional[nanaimo.display.CharacterDisplay]


def _get_display(config: _pytest.config.Config) -> 'nanaimo.display.CharacterDisplay':
    global _display_singleton
    if _display_singleton is None:
        for fixture_type in config.pluginmanager.hook.pytest_nanaimo_fixture_type():
            if fixture_type.get_canonical_name() == 'character_display':
                _display_singleton = fixture_type(nanaimo.fixtures.FixtureManager(asyncio.get_event_loop()))
        if _display_singleton is None:
            raise KeyError('character_display fixture was not found.')
    return _display_singleton


# +---------------------------------------------------------------------------+
# | INTERNALS :: TEST SYNTHESIS (nait mode)
# +---------------------------------------------------------------------------+


_nait_mode = False


def is_nait_mode() -> bool:
    """
    A special mode enabled by the 'nait' commandline that discards all collected tests
    and inserts a single test item driven by nait. This mode is used to interact with
    Nanaimo fixtures from a commandline.
    """
    return _nait_mode


class _NanaimoItem(pytest.Item):
    """
    When running in :func:`is_nait_mode` a single test is synthesized out of this class. The action
    (i.e. :meth:`runtest`) is always executed as the single activity for the invocation.
    """

    nanaimo_results_sneaky_key = '_nanaimo_artifacts'
    """
    An attribute we add to the session's :class:`_pytest.config.Config` instance to store
    fixture artifacts for later reporting in the terminal.
    """

    def __init__(self, parent, fixture_names):
        super().__init__('nanaimo : {}'.format(str(fixture_names)), parent)
        self._logger = logging.getLogger(__name__)
        self._fixture_names = fixture_names

    def on_setup(self) -> None:
        if not hasattr(self.session.config, self.nanaimo_results_sneaky_key):
            setattr(self.session.config, self.nanaimo_results_sneaky_key, dict())

    def runtest(self) -> None:
        """
        Run all fixtures specified on the command-line.
        """
        loop = asyncio.get_event_loop()
        fixtures = []
        nanaimo_defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()
        nanaimo_args = nanaimo.Namespace(self.session.config.option, nanaimo_defaults)
        fixture_manager = PytestFixtureManager(self.config.pluginmanager, loop)
        for fixture_name in self._fixture_names:
            fixtures.append(fixture_manager.create_fixture(fixture_name, nanaimo_args))
        gathers = [asyncio.ensure_future(f.gather()) for f in fixtures]
        results = loop.run_until_complete(asyncio.gather(*gathers, loop=loop))
        combined = nanaimo.Artifacts.combine(*results)
        assert combined.result_code == 0
        getattr(self.session.config, self.nanaimo_results_sneaky_key)[','.join(self._fixture_names)] = combined

    def _prunetraceback(self, excinfo):
        """
        Removes pytest itself from exception traces.
        """
        traceback = excinfo.traceback
        traceback_before_this_item = traceback.cut(path=self.fspath)
        excinfo.traceback = traceback_before_this_item.filter()


# +---------------------------------------------------------------------------+
# | INTERNALS :: PYTEST HOOKS
# +---------------------------------------------------------------------------+


class _SyntheticPlugin:
    """
    Used to synthesize a pytest plugin with the same name as a fixture's canonical name.
    """

    _RemoveInvisiblesPattern = re.compile(r'\.\.\s+invisible-code-block:.*\n(?:[\n]|\s{4,}.*\n)+')

    def __init__(self, fixture_type):
        self._fixture_type = fixture_type

        fixture_type_name = fixture_type.get_canonical_name()

        def _generic_async_fixture(request, nanaimo_fixture_manager):
            fixture = self._create_pytest_fixture(request, nanaimo_fixture_manager, fixture_type)
            if fixture is not None and fixture.get_canonical_name() != request.fixturename:
                raise ValueError('Requested fixture {} but that fixture\'s canonical name is {}'.format(
                    request.fixturename,
                    fixture.get_canonical_name()))
            return fixture

        dedent_docstring = textwrap.dedent(fixture_type.__doc__)
        cleaned_docstring = self._RemoveInvisiblesPattern.sub('', dedent_docstring)
        _generic_async_fixture.__doc__ = cleaned_docstring
        self.__dict__[fixture_type_name] = pytest.fixture(_generic_async_fixture,
                                                          name=fixture_type_name)

    @property
    def fixture_type(self) -> typing.Type['nanaimo.fixtures.Fixture']:
        return self._fixture_type

    def _create_pytest_fixture(self,
                               pytest_request: typing.Any,
                               nanaimo_fixture_manager: nanaimo.fixtures.FixtureManager,
                               fixture_type: typing.Type['nanaimo.fixtures.Fixture']) -> nanaimo.fixtures.Fixture:
        args = pytest_request.config.option
        args_ns = nanaimo.Namespace(args, nanaimo.config.ArgumentDefaults(args), allow_none_values=False)
        return fixture_type(nanaimo_fixture_manager, args_ns)


def pytest_addoption(parser: '_pytest.config.argparsing.Parser', pluginmanager: '_pytest.config.PytestPluginManager')\
        -> None:
    """
    See :func:`_pytest.hookspec.pytest_addoption` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """

    nanaimo_defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()

    nanaimo_options = parser.getgroup('nanaimo',
                                      description='Nanaimo Options')
    nanaimo_options.addoption('--environ', action='append', help='Environment variables to provide to subprocesses as '
                                                                 'a key=value pair')

    nanaimo_options.addoption('--gather-timeout-seconds',
                              type=float,
                              help=textwrap.dedent('''
                            A gather timeout in fractional seconds to use for all fixtures.
                            If not provided then Fixture.gather will not timeout.''').lstrip())

    if is_nait_mode():
        if hasattr(parser, '_usage'):
            # Try to help the user with our hacks by rewriting the usage help string.
            parser._usage = textwrap.dedent('''
                    %(prog)s [options] [nanaimo_fixture] [nanaimo_fixture] [...]

                        *** NOTICE ***
                        When running Nanaimo using %(prog)s the pytest "file_or_dir" positional arguments are
                        interpreted as a list of fixtures to run/gather. Because of this some of the help
                        text emitted from pytest may be misleading.

                        **************
                ''').lstrip()

        nanaimo_options.addoption('--concurrent',
                                  action='store_true',
                                  help=textwrap.dedent('''
                                Run specified fixtures concurrently (i.e. asyncio.gather, NOT multi-threaded).
                                The default is to run/gather each fixture in a separate, synthetic test item.

                            ''').lstrip())

        nanaimo_options.addoption('--environ-shell', '-S', action='store_true', help=textwrap.dedent('''
                                Dump environment variables to stdout as a set of shell commands.
                                Use this to export the subprocess environment for a system to a user
                                shell. For example::

                                    eval $(nait -S)

                            ''').lstrip())

    nanaimo_arguments = nanaimo.Arguments(nanaimo_options, defaults=nanaimo_defaults, filter_duplicates=True)

    # We modify the pytest default behavior here; loading all the plugins here so we are able to visit them
    # so they can contribute options.
    pluginmanager.load_setuptools_entrypoints('pytest11')

    for fixture_type in pluginmanager.hook.pytest_nanaimo_fixture_type():
        pluginmanager.register(_SyntheticPlugin(fixture_type), fixture_type.get_canonical_name())
        group = parser.getgroup(fixture_type.get_canonical_name())
        nanaimo_arguments.set_inner_arguments(group)
        fixture_type.visit_test_arguments(nanaimo_arguments)


def pytest_addhooks(pluginmanager):
    """
    See :func:`_pytest.hookspec.pytest_addhooks` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """
    from nanaimo.pytest import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_collection(session: _pytest.main.Session):
    """
    See :func:`_pytest.hookspec.pytest_collection_modifyitems` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """
    if is_nait_mode():
        f = pytest.File(py.path.local(__file__), session)
        if session.config.option.concurrent:
            session.items = [_NanaimoItem(f, session.config.option.file_or_dir.copy())]
            session.testscollected = 1
        else:
            session.items = []
            for fixture_name in session.config.option.file_or_dir:
                session.items.append(_NanaimoItem(f, [fixture_name]))
            session.testscollected = len(session.items)
        return True


def pytest_sessionstart(session: _pytest.main.Session) -> None:
    """
    See :func:`_pytest.hookspec.pytest_sessionstart` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """
    args = session.config.option
    args_ns = nanaimo.Namespace(args, nanaimo.config.ArgumentDefaults(args), allow_none_values=False)
    nanaimo.set_subprocess_environment(args_ns)
    _get_display(session.config).set_status('busy')


def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    See :func:`_pytest.hookspec.pytest_runtest_setup` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """
    if isinstance(item, _NanaimoItem):
        item.on_setup()
    display = _get_display(item.config)
    display.clear(display_default_message=False)
    display.write(item.name)


def pytest_sessionfinish(session: _pytest.main.Session, exitstatus: int) -> None:
    """
    See :func:`_pytest.hookspec.pytest_sessionfinish` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """
    display = _get_display(session.config)
    display.clear(display_default_message=True)
    display.set_status('okay' if exitstatus == 0 else 'fail')

# +---------------------------------------------------------------------------+
# | INTERNALS :: PYTEST HOOKS :: REPORTING
# +---------------------------------------------------------------------------+


def pytest_report_header(config: _pytest.config.Config, startdir) -> typing.List[str]:
    """
    See :func:`_pytest.hookspec.pytest_sessionfinish` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """
    return ['nait={}'.format(is_nait_mode())]


def pytest_terminal_summary(terminalreporter: '_pytest.terminal.TerminalReporter',
                            exitstatus: int,
                            config: _pytest.config.Config) -> None:
    """
    See :func:`_pytest.hookspec.pytest_sessionfinish` for documentation.
    Also see the "`Writing Plugins <https://docs.pytest.org/en/latest/writing_plugins.html>`_"
    guide.
    """
    terminalreporter.write_sep('-', title='nanaimo', bold=True)
    if hasattr(config, _NanaimoItem.nanaimo_results_sneaky_key):
        results = getattr(config, _NanaimoItem.nanaimo_results_sneaky_key)  # type: typing.Dict[str, nanaimo.Artifacts]
        for fixture_names, artifacts in results.items():
            terminalreporter.write_line('Fixture(s) "{}" result = {}'.format(fixture_names, artifacts.result_code),
                                        green=(artifacts.result_code == 0),
                                        red=(artifacts.result_code != 0))

        for fixture_names, artifacts in results.items():
            terminalreporter.write_sep('.', title='Artifacts for {}'.format(fixture_names), bold=False)
            artifact_vars = vars(artifacts)
            for key, value in artifact_vars.items():
                if not key.startswith('_'):
                    terminalreporter.write_line('{}={}'.format(key, value))
