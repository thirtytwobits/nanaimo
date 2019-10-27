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
Almost everything in Nanaimo is a :class:`Fixture`. Fixtures can be pytest fixtures, instrument
abstractions, aggregates of other fixtures, or anything else that makes sense. The important thing
is that any fixture can be a pytest fixture or can be awaited directly using :ref:`nait`.

"""
import abc
import argparse
import asyncio
import logging
import math
import typing

import pluggy

from .config import ArgumentDefaults


class AssertionError(RuntimeError):
    """
    Thrown by Nanaimo tests when an assertion has failed.

    .. Note::
        This exception should be used only when the state of a :class:`Fixture`
        was invalid. You should use pytest tests and assertions when writing validation
        cases for fixture output like log files or sensor data.
    """
    pass


class Arguments:
    """
    Adapter for pytest and argparse parser arguments.

    :param inner_arguments: Either a pytest group (unpublished type returned from :meth:`pytest.Parser.getgroup`)
        or a :class:`argparse.ArgumentParser`
    :param defaults: Optional provider of default values for arguments.
    """

    def __init__(self, inner_arguments: typing.Any, defaults: typing.Optional[ArgumentDefaults] = None):
        self._inner = inner_arguments
        self._defaults = defaults

    def add_argument(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """
        This method invokes :meth:`argparse.ArgumentParser.add_argument` but with one additional argument:
        ``enable_default_from_environ``. If this is provided as True then a default value will be taken from
        an environment variable derived from the long form of the argument:

        .. invisible-code-block: python
            from nanaimo import Arguments
            from unittest.mock import MagicMock, ANY
            from nanaimo.config import ArgumentDefaults
            import argparse
            import os

            parser = argparse.ArgumentParser()
            parser.add_argument = MagicMock()
            config = ArgumentDefaults()

        .. code-block:: python

            # Using...
            long_arg = '--baud-rate'

            # ...the environment variable looked for will be:
            environment_var_name = 'NANAIMO_BAUD_RATE'

            # If we set the environment variable...
            os.environ[environment_var_name] = '115200'

            a = Arguments(parser, config)

            # ...and provide a default...
            a.add_argument('--baud-rate',
                           default=9600,
                           type=int,
                           enable_default_from_environ=True,
                           help='Will be 9600 unless argument is provided.')

            # ...the actual default value will be 115200

        .. invisible-code-block: python

            parser.add_argument.assert_called_once_with('--baud-rate', default=115200, type=int, help=ANY)

            add_argument_call_args = parser.add_argument.call_args[1]

        .. code-block:: python

            assert add_argument_call_args['default'] == 115200

        """

        if self._defaults is not None:
            self._defaults.populate_default(self._inner, args, kwargs)

        if isinstance(self._inner, argparse.ArgumentParser):
            self._inner.add_argument(*args, **kwargs)
        else:
            self._inner.addoption(*args, **kwargs)


class Namespace:
    """
    Generic object that acts like :class:`argparse.Namespace` but can be created using pytest
    plugin arguments as well.

    If :class:`nanaimo.config.ArgumentDefaults` are used with the :class:`Arguments` and this class then a given
    argument's value will be resolved in the following order:

        1. provided value
        2. config file specified by --rcfile argument.
        3. nanaimo.cfg in user directory
        4. nanaimo.cfg in system directory
        5. default from environment (if ``enable_default_from_environ`` was set for the argument)
        6. default specified for the argument.

    This is accomplished by first rewriting the defaults when attributes are defined on the :class:`Arguments`
    class and then capturing missing attributes on this class and looking up default values from configuration
    files.

    For lookup steps involving configuration files (where :class:`configparser.ConfigParser` is used internally)
    the lookup will search the configuration space using underscores ``_`` as namespace separators. this search
    will proceed as follows:

    .. invisible-code-block: python

        from nanaimo.config import ArgumentDefaults
        from unittest.mock import MagicMock, ANY

        argument_defaults = ArgumentDefaults()
        argument_defaults._configparser = MagicMock()

        values = MagicMock()
        count = 0

        def seventh_times_a_charm(_):
            global count, values
            count += 1
            if count < 7:
                raise KeyError
            return values

        argument_defaults._configparser.__getitem__.side_effect = seventh_times_a_charm

    .. code-block:: python

        # given
        key = 'a_b_c_d'

        # the following lookups will occur
        config_lookups = {
            'nanaimo:a_b_c': 'd',
            'nanaimo:a_b': 'c_d',
            'nanaimo:a': 'b_c_d',
            'a_b_c': 'd',
            'a_b': 'c_d',
            'a': 'b_c_d',
            'nanaimo': 'a_b_c_d'
        }

        # when using an ArgumentDefaults instance
        _ = argument_defaults[key]

    .. invisible-code-block: python

        for item in config_lookups.items():
            argument_defaults._configparser.__getitem__.assert_any_call(item[0])
        values.__getitem__.assert_any_call('a_b_c_d')

    So for a given configuration file::

        [nanaimo]
        a_b_c_d = 1

        [a]
        b_c_d = 2

    the value ``2`` under the ``a`` group will override (i.e. mask) the value ``1`` under the ``nanaimo`` group.

    .. note ::

        A specific example:

        - ``--bk-port <value>`` – if provided on the commandline will always override everything.
        - ``[bk] port = <value>`` – in a config file will be found next if no argument was given on the commandline.
        - ``NANAIMO_BK_PORT`` - set in the environment will be used if no configuration was provided because
          the :mod:`nanaimo.instruments.bkprecision` module defines the ``bk-port`` argument with
          ``enable_default_from_environ`` set.

    """

    def __init__(self,
                 parent: typing.Optional[typing.Any] = None,
                 overrides: typing.Optional[ArgumentDefaults] = None):
        self._overrides = overrides
        if parent is not None:
            for key in vars(parent):
                setattr(self, key, getattr(parent, key))

    def __getattr__(self, key: str) -> typing.Any:
        try:
            return self.__dict__[key]
        except KeyError:
            if self._overrides is None:
                raise
        return self._overrides[key]

    def __contains__(self, key: str) -> typing.Any:
        if key in self.__dict__:
            return True
        elif self._overrides is None:
            return False
        else:
            return key in self._overrides

    def merge(self, **kwargs: typing.Any) -> 'Namespace':
        """
        Merges a list of keyword arguments with this namespace and returns a new, merged
        Namespace. This does not modify the instance that merge is called on.

        Example:

        .. invisible-code-block: python
            from nanaimo import Namespace

        .. code-block:: python

            original = Namespace()
            setattr(original, 'foo', 1)

            assert 1 == original.foo

            merged = original.merge(foo=2, bar='hello')

            assert 1 == original.foo
            assert 2 == merged.foo
            assert 'hello' == merged.bar

        :return: A new namespace with the contents of this object and any values provided as
            kwargs overwriting the values in this instance where the keys are the same.
        """
        merged = Namespace(self, self._overrides)
        for key in kwargs:
            setattr(merged, key, kwargs[key])
        return merged


class Artifacts(Namespace):
    """
    Namespace returned by :class:`Fixture` objects when invoked that contains the artifacts collected
    from the fixture's activities.

    :param result_code: The value to report as the status of the activity that gathered the artifacts.
    :param parent: A parent namespace to lookup in if the current namespace doesn't have a value.
    """

    def __init__(self, result_code: int = 0, parent: typing.Optional[typing.Any] = None):
        super().__init__(parent)
        self._result_code = result_code

    @property
    def result_code(self) -> int:
        """
        0 if the artifacts were retrieved without error. Non-zero if some error
        occurred. The contents of this :class:`Namespace` is undefined for non-zero
        result codes.
        """
        return self._result_code

    @result_code.setter
    def result_code(self, new_result: int) -> None:
        self._result_code = new_result

    def dump(self, logger: logging.Logger, log_level: int = logging.DEBUG) -> None:
        """
        Dump a human readable representation of this object to the given logger.
        :param logger:  The logger to use.
        :param log_level: The log level to dump the object as.
        """
        import yaml
        try:
            logger.log(log_level, yaml.dump(vars(self)))
        except TypeError:
            logger.log(log_level, '(failed to serialize Artifacts)')

    def __int__(self) -> int:
        """
        Converts a reference to this object into its `result_code`.
        """
        return self._result_code


class Fixture(metaclass=abc.ABCMeta):
    """
    Common, abstract class for pytest fixtures based on Nanaimo. Nanaimo fixtures provide a visitor pattern for
    arguments that are common for both pytest extra arguments and for argparse commandline arguments. This allows
    a Nanaimo fixture to expose a direct invocation mode for debuging with the same arguments used by the fixture
    as a pytest plugin. Additionally all Nanaimo fixtures provide a :func:`gather` function that takes a
    :class:`Namespace` containing the provided arguments and returns a set of :class:`Artifacts` gathered by the
    fixture. The contents of these artifacts are documented by each concrete fixture.

    .. invisible-code-block: python
        import nanaimo
        import asyncio

        _doc_loop = asyncio.new_event_loop()

    .. code-block:: python

        class MyFixture(nanaimo.Fixture):
            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                arguments.add_argument('--foo', default='bar')

            async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                artifacts = nanaimo.Artifacts(-1)
                # do something and then return
                artifacts.result_code = 0
                return artifacts

    .. invisible-code-block: python
        foo = MyFixture(nanaimo.FixtureManager(), nanaimo.Namespace(), _doc_loop)

        _doc_loop.run_until_complete(foo.gather())

    `MyFixture` can now be used from a commandline like::

        python -m nanaimo MyFixture --foo baz

    or as part of a pytest::

        pytest --foo=baz

    """

    @classmethod
    def get_canonical_name(cls) -> str:
        """
        The name to use as a key for this :class:`Fixture` type.
        If a class defines a string `fixture_name` this will be used
        as the canonical name otherwise it will be the name of the
        fixture class itself.

        .. invisible-code-block: python
            import nanaimo

        .. code-block:: python

            class MyFixture(nanaimo.Fixture):

                fixture_name = 'my_fixture'

            assert 'my_fixture' == MyFixture.get_canonical_name()

        """
        return str(getattr(cls, 'fixture_name', '.'.join([cls.__module__, cls.__qualname__])))

    def __init__(self,
                 manager: 'FixtureManager',
                 args: Namespace,
                 loop: typing.Optional[asyncio.AbstractEventLoop] = None):
        self._manager = manager
        self._args = args
        self._name = self.get_canonical_name()
        self._logger = logging.getLogger(self._name)
        self._loop = loop

    async def gather(self, **kwargs: typing.Any) -> Artifacts:
        """
        Coroutine awaited to gather a new set of fixture artifacts.

        :param kwargs: Optional arguments to override or augment the arguments provided to the :class:`Fixture`
                       constructor
        :return: A set of artifacts with the :attr:`Artifacts.result_code` set to indicate the success or failure of the
                 fixture's artifact gathering activies.
        """
        return await self.on_gather(self._args.merge(**kwargs))

    # +-----------------------------------------------------------------------+
    # | PROPERTIES
    # +-----------------------------------------------------------------------+
    @property
    def name(self) -> str:
        """
        The canonical name for the Fixture.
        """
        return self._name

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """
        The running asyncio EventLoop in use by this Fixture.
        This will be the loop provided to the fixture in the constructor if that loop is still
        running otherwise the loop will be a running loop retrieved by :func:`asyncio.get_event_loop`.
        :raises RuntimeError: if no running event loop could be found.
        """
        if self._loop is None or not self._loop.is_running():
            self._loop = asyncio.get_event_loop()
        if not self._loop.is_running():
            raise RuntimeError('No running event loop was found!')
        return self._loop

    @property
    def manager(self) -> 'FixtureManager':
        """
        The :class:`FixtureManager` that owns this :class:`Fixture`.
        """
        return self._manager

    @property
    def logger(self) -> logging.Logger:
        """
        A logger for this :class:`Fixture` instance.
        """
        return self._logger

    @property
    def fixture_arguments(self) -> Namespace:
        """
        The Fixture-wide arguments. Can be overridden by kwargs for each :meth:`gather` invocation.
        """
        return self._args

    # +-----------------------------------------------------------------------+
    # | ABSTRACT METHODS
    # +-----------------------------------------------------------------------+
    @classmethod
    @abc.abstractmethod
    def on_visit_test_arguments(cls, arguments: Arguments) -> None:
        """
        Called by the environment before instantiating any :class:`Fixture` instances to register
        arguments supported by each type. These arguments should be portable between both :mod:`argparse`
        and :mod:`pytest`. The fixture is registered for this callback by returning a reference to its
        type from a :attr:`Fixture.Manager.type_factory` annotated function registered as an entrypoint in the Python
        application.
        """
        ...

    @abc.abstractmethod
    async def on_gather(self, args: Namespace) -> Artifacts:
        """
        Coroutine awaited by a call to :meth:`gather`. The fixture should always retrieve new artifacts when invoked
        leaving caching to the caller.

        :param args: The arguments provided for the fixture instance merged with kwargs provided to the :meth:`gather`
            method.
        :type args: Namespace
        :return: A set of artifacts with the :attr:`Artifacts.result_code` set to indicate the success or failure of the
            fixture's artifact gathering activies.
        """
        ...

    # +-----------------------------------------------------------------------+
    # | ASYNC HELPERS
    # +-----------------------------------------------------------------------+

    async def countdown_sleep(self, sleep_time_seconds: float) -> None:
        """
        Calls :func:`asyncio.sleep` for 1 second then emits an :meth:`logging.Logger.info`
        of the time remaining until `sleep_time_seconds`.
        This is useful for long waits as an indication that the process is not deadlocked.

        :param sleep_time_seconds:  The amount of time in seconds for this coroutine to wait
            before exiting. For each second that passes while waiting for this amount of time
            the coroutine will :func:`asyncio.sleep` for 1 second.
        :type sleep_time_seconds: float
        """
        count_down = sleep_time_seconds
        while count_down >= 0:
            self._logger.info('%d', math.ceil(count_down))
            await asyncio.sleep(1)
            count_down -= 1

    async def observe_tasks_assert_not_done(self,
                                            observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future],
                                            timeout_seconds: float,
                                            *args: typing.Union[typing.Coroutine, asyncio.Future]) \
            -> typing.Set[asyncio.Future]:
        """
        Allows running a set of tasks but returning when an observer task completes. This allows a pattern where
        a single task is evaluating the side-effects of other tasks as a gate to continuing the test.
        """
        done, pending = await self._observe_tasks(observer_co_or_f, timeout_seconds, *args)
        if len(done) > 1:
            raise AssertionError('Tasks under observation completed before the observation was complete.')
        return pending

    async def observe_tasks(self,
                            observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future],
                            timeout_seconds: float,
                            *args: typing.Union[typing.Coroutine, asyncio.Future]) -> typing.Set[asyncio.Future]:
        """
        Allows running a set of tasks but returning when an observer task completes. This allows a pattern where
        a single task is evaluating the side-effects of other tasks as a gate to continuing the test.
        """

        done, pending = await self._observe_tasks(observer_co_or_f, timeout_seconds, *args)
        return pending

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+

    async def _observe_tasks(self,
                             observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future],
                             timeout_seconds: float,
                             *args: typing.Union[typing.Coroutine, asyncio.Future]) -> \
            typing.Tuple[typing.Set[asyncio.Future], typing.Set[asyncio.Future]]:

        observing_my_future = asyncio.ensure_future(observer_co_or_f)
        the_children_are_our_futures = [observing_my_future]
        for co_or_f in args:
            the_children_are_our_futures.append(asyncio.ensure_future(co_or_f))

        start_time = self.loop.time()
        wait_timeout = (timeout_seconds if timeout_seconds > 0 else None)

        while True:
            done, pending = await asyncio.wait(
                the_children_are_our_futures,
                timeout=wait_timeout,
                return_when=asyncio.FIRST_COMPLETED)

            if observing_my_future.done():
                return done, pending

            if wait_timeout is not None and self.loop.time() - start_time > wait_timeout:
                break

        raise asyncio.TimeoutError()


class FixtureManager:
    """
    A simple fixture manager and a baseclass for specalized managers.
    """

    def __init__(self) -> None:
        self._fixture_cache = dict()  # type: typing.Dict[str, Fixture]

    def fixture_types(self) -> typing.Generator:
        """
        Yields each fixture type registered with this object. The types may or may not
        have already been instantiated.
        """
        if False:
            yield

    def get_fixture(self, fixture_name: str) -> Fixture:
        """
        Get a fixture instance if it was already created for this manager.

        :param fixture_name: The canonical name of the fixture.
        :type fixture_name: str
        :return: A manager-scoped fixture instance (i.e. One-and-only-one
            fixture instance with this name for this manager object).
        :raises KeyError: if fixture_name was not instantiated.
        """
        return self._fixture_cache[fixture_name]

    def create_fixture(self,
                       fixture_name: str,
                       args: Namespace,
                       loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> Fixture:
        raise NotImplementedError('The base class is an incomplete implementation.')


class PluggyFixtureManager(FixtureManager):
    """
    Object that scopes a set of :class:`Fixture` objects discovered using
    `pluggy <https://pluggy.readthedocs.io/en/latest/>`_.
    """

    plugin_name = 'nanaimo'

    type_factory_spec = pluggy.HookspecMarker(plugin_name)
    type_factory = pluggy.HookimplMarker(plugin_name)

    def __init__(self) -> None:
        super().__init__()
        self._pluginmanager = pluggy.PluginManager(self.plugin_name)

        class PluginNamespace:
            @self.type_factory_spec
            def get_fixture_type(self) -> typing.Type['Fixture']:
                raise NotImplementedError()

        self._pluginmanager.add_hookspecs(PluginNamespace)
        self._pluginmanager.load_setuptools_entrypoints(self.plugin_name)

    def fixture_types(self) -> typing.Generator:
        for fixture_type in self._pluginmanager.hook.get_fixture_type():
            yield fixture_type

    def create_fixture(self,
                       fixture_name: str,
                       args: Namespace,
                       loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> Fixture:
        for fixture_type in self._pluginmanager.hook.get_fixture_type():
            if fixture_type.get_canonical_name() == fixture_name:
                fixture = typing.cast(Fixture, fixture_type(self, args, loop))
                self._fixture_cache[fixture_name] = fixture
                return fixture
        raise KeyError(fixture_name)
