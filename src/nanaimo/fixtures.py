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
Almost everything in Nanaimo is a :class:`nanaimo.fixtures.Fixture`. Fixtures can be pytest fixtures, instrument
abstractions, aggregates of other fixtures, or anything else that makes sense. The important thing
is that any fixture can be a pytest fixture or can be awaited directly using :ref:`nait`.
"""
import abc
import asyncio
import io
import logging
import math
import typing

import pluggy

import nanaimo


class Fixture(metaclass=abc.ABCMeta):
    """
    Common, abstract class for pytest fixtures based on Nanaimo. Nanaimo fixtures provide a visitor pattern for
    arguments that are common for both pytest extra arguments and for argparse commandline arguments. This allows
    a Nanaimo fixture to expose a direct invocation mode for debuging with the same arguments used by the fixture
    as a pytest plugin. Additionally all Nanaimo fixtures provide a :func:`gather` function that takes a
    :class:`nanaimo.Namespace` containing the provided arguments and returns a set of :class:`nanaimo.Artifacts`
    gathered by the fixture. The contents of these artifacts are documented by each concrete fixture.

    .. invisible-code-block: python

        import nanaimo
        import nanaimo.fixtures
        import asyncio

        _doc_loop = asyncio.new_event_loop()

    .. code-block:: python

        class MyFixture(nanaimo.fixtures.Fixture):
            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                arguments.add_argument('--foo', default='bar')

            async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                artifacts = nanaimo.Artifacts(-1)
                # do something and then return
                artifacts.result_code = 0
                return artifacts

    .. invisible-code-block: python

        foo = MyFixture(nanaimo.fixtures.FixtureManager(), nanaimo.Namespace(), loop=_doc_loop)

        _doc_loop.run_until_complete(foo.gather())

    `MyFixture` can now be used from a commandline like::

        python -m nanaimo MyFixture --foo baz

    or as part of a pytest::

        pytest --foo=baz

    :param FixtureManager manager: The fixture manager that is the scope for this fixture. There must be
        a 1:1 relationship between a fixture instance and a fixture manager instance.
    :param nanaimo.Namespace args: A namespace containing the arguments for this fixture.
    :param kwargs: All fixtures can be given a :class:`asyncio.AbstractEventLoop` instance to use as ``loop`` and
        an initial value for :data:`gather_timeout_seconds` as ``gather_timeout_seconds (float)``. Other keyword
        arguments may used by fixture specializations.
    """

    @classmethod
    def get_canonical_name(cls) -> str:
        """
        The name to use as a key for this :class:`nanaimo.fixtures.Fixture` type.
        If a class defines a string `fixture_name` this will be used
        as the canonical name otherwise it will be the name of the
        fixture class itself.

        .. invisible-code-block: python
            import nanaimo
            import nanaimo.fixtures

        .. code-block:: python

            class MyFixture(nanaimo.fixtures.Fixture):

                fixture_name = 'my_fixture'

            assert 'my_fixture' == MyFixture.get_canonical_name()

        """
        return str(getattr(cls, 'fixture_name', '.'.join([cls.__module__, cls.__qualname__])))

    @classmethod
    def get_argument_prefix(cls) -> str:
        """
        The name to use as a prefix for arguments. This also becomes the configuration
        section that the fixture's arguments can be overridden from. If the fixture
        defines an ``argument_prefix`` class member this value is used otherwise the
        value returned from :meth:`get_canonical_name` is used.

        .. invisible-code-block: python
            import nanaimo
            import nanaimo.fixtures

        .. code-block:: python

            class MyFixture(nanaimo.fixtures.Fixture):

                argument_prefix = 'mf'

        >>> MyFixture.get_argument_prefix()  # noqa : F821
        'mf'

        .. code-block:: python

            class MyOtherFixture(nanaimo.fixtures.Fixture):
                # this class doesn't define argument_prefix so
                # so the canonical name is used instead.
                fixture_name = 'my_outre_fixture'

        >>> MyOtherFixture.get_argument_prefix()  # noqa : F821
        'my-outre-fixture'

        """
        return str(getattr(cls, 'argument_prefix', cls.get_canonical_name().replace('_', '-')))

    def __init__(self,
                 manager: 'FixtureManager',
                 args: typing.Optional[nanaimo.Namespace] = None,
                 **kwargs: typing.Any):
        self._manager = manager
        self._args = (args if args is not None else nanaimo.Namespace())
        self._name = self.get_canonical_name()
        self._logger = logging.getLogger(self._name)
        if 'loop' in kwargs:
            self._loop = typing.cast(typing.Optional[asyncio.AbstractEventLoop], kwargs['loop'])
        else:
            self._loop = None
        if 'gather_timeout_seconds' in kwargs:
            gather_timeout_seconds = typing.cast(typing.Optional[float], kwargs['gather_timeout_seconds'])
            self._gather_timeout_seconds = (gather_timeout_seconds if gather_timeout_seconds is not None else 0)
        else:
            self._gather_timeout_seconds = 0

    async def gather(self, *args: typing.Any, **kwargs: typing.Any) -> nanaimo.Artifacts:
        """
        Coroutine awaited to gather a new set of fixture artifacts.

        :param kwargs: Optional arguments to override or augment the arguments provided to the
            :class:`nanaimo.fixtures.Fixture` constructor
        :return: A set of artifacts with the :attr:`nanaimo.Artifacts.result_code` set to indicate the success or
                 failure of the fixture's artifact gathering activies.
        :raises asyncio.TimeoutError: If :data:`gather_timeout_seconds` is > 0 and :meth:`on_gather` takes longer
            then this to complete or if on_gather itself raises a timeout error.
        """
        pushed_args = self._args
        self._args = self._args.merge(**kwargs)
        try:
            routine = self.on_gather(self._args)
            if self._gather_timeout_seconds > 0:
                done, pending = await asyncio.wait([asyncio.ensure_future(routine)],
                                                   loop=self.manager.loop,
                                                   timeout=self._gather_timeout_seconds,
                                                   return_when=asyncio.ALL_COMPLETED)
                if len(pending) > 0:
                    pending.pop().cancel()
                    raise asyncio.TimeoutError('{} gather was cancelled after waiting for {} seconds'
                                               .format(self.get_canonical_name(),
                                                       self._gather_timeout_seconds))
                return done.pop().result()
            else:
                return await routine
        finally:
            self._args = pushed_args

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
            self._loop = self.manager.loop
        if not self._loop.is_running():
            raise RuntimeError('No running event loop was found!')
        return self._loop

    @property
    def manager(self) -> 'FixtureManager':
        """
        The :class:`FixtureManager` that owns this :class:`nanaimo.fixtures.Fixture`.
        """
        return self._manager

    @property
    def logger(self) -> logging.Logger:
        """
        A logger for this :class:`nanaimo.fixtures.Fixture` instance.
        """
        return self._logger

    @property
    def fixture_arguments(self) -> nanaimo.Namespace:
        """
        The Fixture-wide arguments. Can be overridden by kwargs for each :meth:`gather` invocation.
        """
        return self._args

    @property
    def gather_timeout_seconds(self) -> float:
        """
        The timeout in fractional seconds to wait for :meth:`on_gather` to complete before raising
        a :class:`asyncio.TimeoutError`.
        """
        return self._gather_timeout_seconds

    @gather_timeout_seconds.setter
    def gather_timeout_seconds(self, gather_timeout_seconds: float) -> None:
        self._gather_timeout_seconds = gather_timeout_seconds

    # +-----------------------------------------------------------------------+
    # | ABSTRACT METHODS
    # +-----------------------------------------------------------------------+
    @classmethod
    @abc.abstractmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        """
        Called by the environment before instantiating any :class:`nanaimo.fixtures.Fixture` instances to register
        arguments supported by each type. These arguments should be portable between both :mod:`argparse`
        and ``pytest``. The fixture is registered for this callback by returning a reference to its
        type from a :attr:`PluggyFixtureManager.type_factory` annotated function registered as an
        entrypoint in the Python application.
        """
        ...

    @abc.abstractmethod
    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        Coroutine awaited by a call to :meth:`gather`. The fixture should always retrieve new artifacts when invoked
        leaving caching to the caller.

        :param args: The arguments provided for the fixture instance merged with kwargs provided to the :meth:`gather`
            method.
        :type args: nanaimo.Namespace
        :return: A set of artifacts with the :attr:`nanaimo.Artifacts.result_code` set to indicate the success or
            failure of the fixture's artifact gathering activies.
        :raises asyncio.TimeoutError: It is valid for a fixture to raise timeout errors from this method.
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
                                            *persistent_tasks: typing.Union[typing.Coroutine, asyncio.Future]) \
            -> typing.Set[asyncio.Future]:
        """
        Allows running a set of tasks but returning when an observer task completes. This allows a pattern where
        a single task is evaluating the side-effects of other tasks as a gate to continuing the test.

        :param observer_co_or_f: The task that is expected to complete in less than ``timeout_seconds``.
        :type observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future]
        :param float timeout_seconds: Time in seconds to observe for before raising :class:`asyncio.TimeoutError`.
            Set to 0 to disable.
        :param persistent_tasks: Iterable of tasks that must remain active or :class:`AssertionError` will be raised.
        :type persistent_tasks: typing.Union[typing.Coroutine, asyncio.Future]

        :return: a list of the persistent tasks as futures.
        :rtype: typing.Set[asyncio.Future]

        :raises AssertionError: if any of the persistent tasks exited.
        :raises asyncio.TimeoutError: if the observer task does not complete within ``timeout_seconds``.
        """
        _, _, done, pending = await self._observe_tasks(observer_co_or_f, timeout_seconds, False, *persistent_tasks)
        if len(done) > 1:
            raise nanaimo.AssertionError('Tasks under observation completed before the observation was complete.')
        return pending

    async def observe_tasks(self,
                            observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future],
                            timeout_seconds: float,
                            *persistent_tasks: typing.Union[typing.Coroutine, asyncio.Future]) \
            -> typing.Set[asyncio.Future]:
        """
        Allows running a set of tasks but returning when an observer task completes. This allows a pattern where
        a single task is evaluating the side-effects of other tasks as a gate to continuing the test or simply
        that a set of task should continue to run but a single task must complete.

        :param observer_co_or_f: The task that is expected to complete in less than ``timeout_seconds``.
        :type observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future]
        :param float timeout_seconds: Time in seconds to observe for before raising :class:`asyncio.TimeoutError`.
            Set to 0 to disable.
        :param persistent_tasks: Iterable of tasks that may remain active.
        :type persistent_tasks: typing.Union[typing.Coroutine, asyncio.Future]

        :return: a list of the persistent tasks as futures.
        :rtype: typing.Set[asyncio.Future]

        :raises AssertionError: if any of the persistent tasks exited.
        :raises asyncio.TimeoutError: if the observer task does not complete within ``timeout_seconds``.
        """

        _, _, done, pending = await self._observe_tasks(observer_co_or_f, timeout_seconds, False, *persistent_tasks)
        return pending

    async def gate_tasks(self,
                         gate_co_or_f: typing.Union[typing.Coroutine, asyncio.Future],
                         timeout_seconds: float,
                         *gated_tasks: typing.Union[typing.Coroutine, asyncio.Future]) \
            -> typing.Tuple[asyncio.Future, typing.List[asyncio.Future]]:
        """
        Runs a set of tasks until a gate task completes then cancels the remaining tasks.

        .. invisible-code-block: python

            from nanaimo.fixtures import FixtureManager
            from nanaimo.builtin import nanaimo_bar
            import asyncio

            loop = asyncio.get_event_loop()
            manager = FixtureManager(loop=loop)

        .. code-block:: python

            async def gated_task():
                while True:
                    await asyncio.sleep(.1)

            async def gate_task():
                await asyncio.sleep(1)
                return 'gate passed'

            async def example():

                any_fixture = nanaimo_bar.Fixture(manager)

                gate_future, gated_futures = await any_fixture.gate_tasks(gate_task(), 0, gated_task())

                assert not gate_future.cancelled()
                assert 'gate passed' == gate_future.result()
                assert len(gated_futures) == 1
                assert gated_futures[0].cancelled()

        .. invisible-code-block: python

            loop.run_until_complete(example())

        :param gate_co_or_f: The task that is expected to complete in less than ``timeout_seconds``.
        :type gate_co_or_f: typing.Union[typing.Coroutine, asyncio.Future]
        :param float timeout_seconds: Time in seconds to wait for the gate for before raising
            :class:`asyncio.TimeoutError`. Set to 0 to disable.
        :param persistent_tasks: Iterable of tasks that may remain active.
        :type persistent_tasks: typing.Union[typing.Coroutine, asyncio.Future]

        :return: a tuple of the gate future and a set of the gated futures.
        :rtype: typing.Tuple[asyncio.Future, typing.Set[asyncio.Future]]:

        :raises AssertionError: if any of the persistent tasks exited.
        :raises asyncio.TimeoutError: if the observer task does not complete within ``timeout_seconds``.
        """

        observer, observed, _, _ = await self._observe_tasks(gate_co_or_f, timeout_seconds, True, *gated_tasks)
        return observer, observed

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+
    @classmethod
    async def _do_cancel_remaining(cls, pending: typing.Set[asyncio.Future]) -> None:
        for f in pending:
            f.cancel()
            try:
                await f
            except asyncio.CancelledError:
                pass

    async def _observe_tasks(self,
                             observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future],
                             timeout_seconds: float,
                             cancel_remaining: bool,
                             *args: typing.Union[typing.Coroutine, asyncio.Future]) -> \
            typing.Tuple[asyncio.Future, typing.List[asyncio.Future],
                         typing.Set[asyncio.Future], typing.Set[asyncio.Future]]:
        """
        :returns: observer, observed, done, pending
        """
        did_timeout = False
        observer_future = asyncio.ensure_future(observer_co_or_f)
        the_children_are_our_futures = [observer_future]
        observed_futures = []
        done_done = set()  # type: typing.Set[asyncio.Future]
        for co_or_f in args:
            o = asyncio.ensure_future(co_or_f)
            the_children_are_our_futures.append(o)
            observed_futures.append(o)

        start_time = self.loop.time()
        wait_timeout = (timeout_seconds if timeout_seconds > 0 else None)

        while True:
            done, pending = await asyncio.wait(
                the_children_are_our_futures,
                timeout=wait_timeout,
                return_when=asyncio.FIRST_COMPLETED)

            for d in done:
                the_children_are_our_futures.remove(d)
                done_done.add(d)

            if observer_future.done():
                break

            if wait_timeout is not None and self.loop.time() - start_time > wait_timeout:
                did_timeout = True
                break

        if cancel_remaining:
            await self._do_cancel_remaining(pending)
            done_done.update(pending)
            pending.clear()

        if did_timeout:
            raise asyncio.TimeoutError()
        else:
            return observer_future, observed_futures, done_done, pending


# +---------------------------------------------------------------------------+


class SubprocessFixture(Fixture):
    """
    Fixture base type that accepts a string argument ``cmd`` and executes it as a subprocess.
    """

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        +--------------+---------------------------+-----------------------------------------------+
        | **Returned Artifacts**                                                                   |
        +--------------+---------------------------+-----------------------------------------------+
        | key          | type                      | Notes                                         |
        +==============+===========================+===============================================+
        | logfile      | Optional[str]             | A file to log to. Set this in                 |
        |              |                           | on_construct_command and this baseclass will  |
        |              |                           | multiplex all stdout and stderr to the file.  |
        +--------------+---------------------------+-----------------------------------------------+
        | stderr       | Optional[str]             | Capture of stderr                             |
        +--------------+---------------------------+-----------------------------------------------+
        | stdout       | Optional[str]             | Capture of stdout                             |
        +--------------+---------------------------+-----------------------------------------------+
        """
        artifacts = nanaimo.Artifacts()

        cmd = self.on_construct_command(args, artifacts)

        logfile_handler = None  # type: typing.Optional[logging.FileHandler]
        if artifacts.logfile is not None:
            logfile_handler = logging.FileHandler(filename=str(artifacts.logfile), mode='a')
            file_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(name)s: %(message)s',
                                               datefmt='%Y-%m-%d %H:%M:%S')
            logfile_handler.setFormatter(file_formatter)
            self._logger.addHandler(logfile_handler)

        try:
            self._logger.debug('About to execute command "%s" in a subprocess shell', cmd)

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )  # type: asyncio.subprocess.Process

            stdout, stderr = await self._wait_for_either_until_neither(
                (proc.stdout if proc.stdout is not None else self._NoopStreamReader()),
                (proc.stderr if proc.stderr is not None else self._NoopStreamReader()))

            await proc.wait()

            self._logger.debug('command "%s" exited with %i', cmd, proc.returncode)

            setattr(artifacts, 'stdout', stdout)
            setattr(artifacts, 'stderr', stderr)

            artifacts.result_code = proc.returncode
            return artifacts
        finally:
            if logfile_handler is not None:
                self._logger.removeHandler(logfile_handler)

    # +-----------------------------------------------------------------------+
    # | ABSTRACT METHODS
    # +-----------------------------------------------------------------------+
    @abc.abstractmethod
    def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        """
        Called by the subprocess fixture to ask the specialization to form a command
        given a set of arguments.

        :param arguments: The arguments passed into :meth:`Fixture.on_gather`.
        :type arguments: nanaimo.Arguments
        :param inout_artifacts: A set of artifacts the superclass is assembling This
            is provided to the subclass to allow it to optionally contribute artifacts.
        :type inout_artifacts: nanaimo.Artifacts
        :return: The command to run in a subprocess shell.
        """
        ...

    # +-----------------------------------------------------------------------+
    # | PRIVATE METHODS
    # +-----------------------------------------------------------------------+

    class _NoopStreamReader(asyncio.StreamReader):

        def __init__(self) -> None:
            super().__init__()
            self.feed_eof()

    async def _wait_for_either_until_neither(self,
                                             stdout: asyncio.StreamReader,
                                             stderr: asyncio.StreamReader) \
            -> typing.Tuple[str, str]:
        """
        Wait for a line of data from either stdout or stderr and log this data as received.
        When both are EOF then exit.

        :returns: Tuple of stdout, stderr
        """
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        future_out = asyncio.ensure_future(stdout.readline())
        future_err = asyncio.ensure_future(stderr.readline())

        pending = set([future_out, future_err])

        while len(pending) > 0:

            done, pending = await asyncio.wait(pending)

            for future_done in done:
                result = future_done.result().strip()
                if len(result) > 0:
                    line = result.decode()
                    if future_done == future_err:
                        future_err = asyncio.ensure_future(stderr.readline())
                        pending.add(future_err)
                        stderr_buffer.write(line)
                        self._logger.error(line)
                    else:
                        future_out = asyncio.ensure_future(stdout.readline())
                        pending.add(future_out)
                        stdout_buffer.write(line)
                        self._logger.info(line.strip())
        return (stdout_buffer.getvalue(), stderr_buffer.getvalue())


# +---------------------------------------------------------------------------+


class FixtureManager:
    """
    A simple fixture manager and a baseclass for specalized managers.
    """

    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._loop = loop

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """
        The running asyncio EventLoop in use by all Fixtures.
        This will be the loop provided to the fixture manager in the constructor if that loop is still
        running otherwise the loop will be a running loop retrieved by :func:`asyncio.get_event_loop`.
        :raises RuntimeError: if no running event loop could be found.
        """
        if self._loop is None or not self._loop.is_running():
            self._loop = asyncio.get_event_loop()
        if not self._loop.is_running():
            raise RuntimeError('No running event loop was found!')
        return self._loop

    def fixture_types(self) -> typing.Generator:
        """
        Yields each fixture type registered with this object.
        """
        if False:
            yield

    def create_fixture(self,
                       canonical_name: str,
                       args: typing.Optional[nanaimo.Namespace] = None,
                       loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> Fixture:
        """
        Create a new :class:`nanaimo.fixtures.Fixture` instance iff the ``canonical_name``` is a registered
        plugin for this process.

        :param str canonical_name: The canonical name of the fixture to instantiate.
        :param nanaimo.Namespace args: The arguments to provide to the new instance.
        :param loop: An event loop to provide the fixture instance.
        :type loop: typing.Optional[asyncio.AbstractEventLoop]
        :raises KeyError: if ``canonical_name`` was not registered with this manager.
        """
        raise NotImplementedError('The base class is an incomplete implementation.')


class PluggyFixtureManager(FixtureManager):
    """
    Object that scopes a set of :class:`nanaimo.fixtures.Fixture` objects discovered using
    `pluggy <https://pluggy.readthedocs.io/en/latest/>`_.
    """

    plugin_name = 'nanaimo'

    type_factory_spec = pluggy.HookspecMarker(plugin_name)
    type_factory = pluggy.HookimplMarker(plugin_name)

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._pluginmanager = pluggy.PluginManager(self.plugin_name)

        class PluginNamespace:
            @self.type_factory_spec
            def get_fixture_type(self) -> typing.Type['Fixture']:
                raise NotImplementedError()

        self._pluginmanager.add_hookspecs(PluginNamespace)
        self._pluginmanager.load_setuptools_entrypoints(self.plugin_name)

        prefix_map = dict()  # type: typing.Dict
        self._blacklist = set()  # type: typing.Set
        for fixture_type in self._pluginmanager.hook.get_fixture_type():
            fap = fixture_type.get_argument_prefix()
            if fap in prefix_map:
                self._blacklist.add(fixture_type.get_canonical_name())
                self._logger.error('Argument prefix {} was already registered by {}! Fixture {} will not be available.'
                                   .format(fap, prefix_map[fap], fixture_type.get_canonical_name()))
            else:
                prefix_map[fap] = fixture_type.get_canonical_name()

    def fixture_types(self) -> typing.Generator:
        for fixture_type in self._pluginmanager.hook.get_fixture_type():
            if fixture_type.get_canonical_name() not in self._blacklist:
                yield fixture_type

    def create_fixture(self,
                       canonical_name: str,
                       args: typing.Optional[nanaimo.Namespace] = None,
                       loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> Fixture:
        for fixture_type in self.fixture_types():
            if fixture_type.get_canonical_name() == canonical_name:
                fixture = typing.cast(Fixture, fixture_type(self, args, loop=loop))
                return fixture
        raise KeyError(canonical_name)
