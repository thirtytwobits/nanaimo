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
import textwrap
import typing

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

        foo = MyFixture(nanaimo.fixtures.FixtureManager(_doc_loop), nanaimo.Namespace())

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

    @classmethod
    def get_arg_covariant(cls,
                          args: nanaimo.Namespace,
                          base_name: str,
                          default_value: typing.Optional[typing.Any] = None) -> typing.Any:
        """
        When called by a baseclass this method will return the most specalized argument value
        available.

        :param args: The arguments to search.
        :param base_name: The base name. For example ``foo`` for ``--prefix-bar``.
        :param default_value: The value to use if the argument could not be found.
        """

        prefix = cls.get_argument_prefix().replace('-', '_')
        if len(prefix) > 0:
            prefix += '_'
        full_key = '{}{}'.format(prefix, base_name.replace('-', '_'))
        result = getattr(args, full_key)
        if result is None:
            return default_value
        else:
            return result

    @classmethod
    def get_arg_covariant_or_fail(cls, args: nanaimo.Namespace, base_name: str) -> typing.Any:
        """
        Calls :meth:`get_arg_covariant` but raises :class:`ValueError` if the result is `None`.

        :raises ValueError: if no value could be found for the argument.
        """
        optional_result = cls.get_arg_covariant(args, base_name)
        if optional_result is None:
            raise ValueError('{base_name} argument not provided (--[argument prefix]-{base_name}'
                             .format(base_name=base_name))
        return optional_result

    def __init__(self,
                 manager: 'FixtureManager',
                 args: typing.Optional[nanaimo.Namespace] = None,
                 **kwargs: typing.Any):
        self._manager = manager
        self._args = (args if args is not None else nanaimo.Namespace())
        self._name = self.get_canonical_name()
        self._logger = logging.getLogger(self._name)
        if 'loop' in kwargs:
            print('WARNING: Passing loop into Fixture is deprecated. (This will be an exception in a future release).')
        if 'gather_timeout_seconds' in kwargs:
            gather_timeout_seconds = typing.cast(typing.Optional[float], kwargs['gather_timeout_seconds'])
            self._gather_timeout_seconds = gather_timeout_seconds
        else:
            self._gather_timeout_seconds = None

    def gather_until_complete(self, *args: typing.Any, **kwargs: typing.Any) -> nanaimo.Artifacts:
        """
        helper function where this:

        .. invisible-code-block: python

            import nanaimo
            import nanaimo.fixtures
            import asyncio

            _doc_loop = asyncio.new_event_loop()

            class MyFixture(nanaimo.fixtures.Fixture):

                @classmethod
                def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                    pass

                async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                    artifacts = nanaimo.Artifacts(0)
                    return artifacts

            foo = MyFixture(nanaimo.fixtures.FixtureManager(_doc_loop), nanaimo.Namespace())

        .. code-block:: python

            foo.gather_until_complete()

        is equivalent to this:

        .. code-block:: python

            foo.loop.run_until_complete(foo.gather())

        """
        return self.loop.run_until_complete(self.gather(*args, **kwargs))

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
            routine = self.on_gather(self._args)  # type: typing.Coroutine
            if self._gather_timeout_seconds is not None:
                done, pending = await asyncio.wait([asyncio.ensure_future(routine)],
                                                   loop=self.loop,
                                                   timeout=self._gather_timeout_seconds,
                                                   return_when=asyncio.ALL_COMPLETED)  \
                    # type: typing.Set[asyncio.Future], typing.Set[asyncio.Future]
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
        return self.manager.loop

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
    def gather_timeout_seconds(self) -> typing.Optional[float]:
        """
        The timeout in fractional seconds to wait for :meth:`on_gather` to complete before raising
        a :class:`asyncio.TimeoutError`.
        """
        return self._gather_timeout_seconds

    @gather_timeout_seconds.setter
    def gather_timeout_seconds(self, gather_timeout_seconds: float) -> None:
        self._gather_timeout_seconds = gather_timeout_seconds

    @classmethod
    def visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        """
        Visit this fixture's :meth:`on_visit_test_arguments` but with the
        proper :data:`nanaimo.Arguments.required_prefix` set.
        """

        previous_required_prefix = arguments.required_prefix
        arguments.required_prefix = cls.get_argument_prefix().replace('_', '-')
        cls.on_visit_test_arguments(arguments)
        arguments.required_prefix = previous_required_prefix

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
        type from a ``pytest_nanaimo_fixture_type`` hook in your fixture's pytest plugin module.
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
                                            timeout_seconds: typing.Optional[float],
                                            *persistent_tasks: typing.Union[typing.Coroutine, asyncio.Future]) \
            -> typing.Set[asyncio.Future]:
        """
        Allows running a set of tasks but returning when an observer task completes. This allows a pattern where
        a single task is evaluating the side-effects of other tasks as a gate to continuing the test.

        :param observer_co_or_f: The task that is expected to complete in less than ``timeout_seconds``.
        :type observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future]
        :param float timeout_seconds: Time in seconds to observe for before raising :class:`asyncio.TimeoutError`.
            Set to None to disable.
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
                            timeout_seconds: typing.Optional[float],
                            *persistent_tasks: typing.Union[typing.Coroutine, asyncio.Future]) \
            -> typing.Set[asyncio.Future]:
        """
        Allows running a set of tasks but returning when an observer task completes. This allows a pattern where
        a single task is evaluating the side-effects of other tasks as a gate to continuing the test or simply
        that a set of task should continue to run but a single task must complete.

        :param observer_co_or_f: The task that is expected to complete in less than ``timeout_seconds``.
        :type observer_co_or_f: typing.Union[typing.Coroutine, asyncio.Future]
        :param float timeout_seconds: Time in seconds to observe for before raising :class:`asyncio.TimeoutError`.
            Set to None to disable.
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
                         timeout_seconds: typing.Optional[float],
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

                gate_future, gated_futures = await any_fixture.gate_tasks(gate_task(), None, gated_task())

                assert not gate_future.cancelled()
                assert 'gate passed' == gate_future.result()
                assert len(gated_futures) == 1
                assert gated_futures[0].cancelled()

        .. invisible-code-block: python

            loop.run_until_complete(example())

        :param gate_co_or_f: The task that is expected to complete in less than ``timeout_seconds``.
        :type gate_co_or_f: typing.Union[typing.Coroutine, asyncio.Future]
        :param float timeout_seconds: Time in seconds to wait for the gate for before raising
            :class:`asyncio.TimeoutError`. Set to None to disable.
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
                             timeout_seconds: typing.Optional[float],
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

        while True:
            done, pending = await asyncio.wait(
                the_children_are_our_futures,
                timeout=timeout_seconds,
                return_when=asyncio.FIRST_COMPLETED)  # type: typing.Set[asyncio.Future], typing.Set[asyncio.Future]

            for d in done:
                the_children_are_our_futures.remove(d)
                done_done.add(d)

            if observer_future.done():
                break

            if timeout_seconds is not None and self.loop.time() - start_time > timeout_seconds:
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
    Because some subprocess commands might result in huge amounts of data being sent to stdout
    and/or stderr this class does not capture this data by default. Instead, tests are encouraged
    to either filter the subprocess pipes or use the ``--logfile`` argument to write the output
    to a file in persistent storage.

    Filtering is accomplished using the :data:`stdout_filter <nanaimo.fixtures.SubprocessFixture.stdout_filter>`
    or :data:`stderr_filter <nanaimo.fixtures.SubprocessFixture.stderr_filter>` property of this class.
    For example:

    .. invisible-code-block: python
        import nanaimo.version
        import asyncio

        loop = asyncio.get_event_loop()
        manager = nanaimo.fixtures.FixtureManager(loop=loop)

    .. code-block:: python

        class MySubprocessFixture(nanaimo.fixtures.SubprocessFixture):
            '''
            Subprocess test fixture that simply calls "nait --version"
            '''

            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                pass

            def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
                return 'nait --version'


        async def example(manager):

            subject = MySubprocessFixture(manager)

            # The accumulator does capture all stdout. Only use this if you know
            # the subprocess will produce a managable and bounded amount of output.
            filter = nanaimo.fixtures.SubprocessFixture.SubprocessMessageAccumulator()
            subject.stdout_filter = filter

            artifacts = await subject.gather()

            # In our example the subprocess produces only and exactly the Nanaimo
            # version number
            assert filter.getvalue() == nanaimo.version.__version__

    .. invisible-code-block: python

        loop.run_until_complete(example(manager))


    :param stdout_filter: A :class:`logging.Filter` used when gathering the subprocess.
    :param stderr_filter: A :class:`logging.Filter` used when gathering the subprocess.
    """

    class SubprocessMessageAccumulator(logging.Filter, io.StringIO):
        """
        Helper class for working with :meth:`SubprocessFixture.stdout_filter` or
        :meth:`SubprocessFixture.stderr_filter`. This implementation will simply
        write all log messages (i.e. :meth:`logging.LogRecord.getMessage()`) to
        its internal buffer. Use :meth:`getvalue()` to get a reference to the
        buffer.

        You can also subclass this method and override its :meth:`logging.Filter.filter`
        method to customize your filter criteria.

        :param minimum_level: The minimum loglevel to accumulate messages for.
        """

        def __init__(self, minimum_level: int = logging.INFO):
            logging.Filter.__init__(self)
            io.StringIO.__init__(self)
            self._minimum_level = minimum_level

        def filter(self, record: logging.LogRecord) -> bool:
            if record.levelno >= self._minimum_level:
                self.write(record.getMessage())
            return True

    class SubprocessMessageMatcher(logging.Filter):
        """
        Helper class for working with :meth:`SubprocessFixture.stdout_filter` or
        :meth:`SubprocessFixture.stderr_filter`. This implementation will watch every
        log message and store any that match the provided pattern.

        This matcher does not buffer all logged messages.

        :param pattern: A regular expression to match messages on.
        :param minimum_level: The minimum loglevel to accumulate messages for.
        """

        def __init__(self, pattern: typing.Any, minimum_level: int = logging.INFO):
            logging.Filter.__init__(self)
            self._pattern = pattern
            self._minimum_level = minimum_level
            self._matches = []  # type: typing.List

        @property
        def match_count(self) -> int:
            """
            The number of messages that matched the provided pattern.
            """
            return len(self._matches)

        @property
        def matches(self) -> typing.List:
            return self._matches

        def filter(self, record: logging.LogRecord) -> bool:
            if record.levelno >= self._minimum_level:
                match = self._pattern.match(record.getMessage())
                if match is not None:
                    self._matches.append(match)
            return True

    def __init__(self,
                 manager: 'FixtureManager',
                 args: typing.Optional[nanaimo.Namespace] = None,
                 **kwargs: typing.Any):
        super().__init__(manager, args, **kwargs)
        self._stdout_filter = None  # type: typing.Optional[logging.Filter]
        self._stderr_filter = None  # type: typing.Optional[logging.Filter]
        if 'stdout_filter' in kwargs:
            self._stdout_filter = kwargs['stdout_filter']
        if 'stderr_filter' in kwargs:
            self._stderr_filter = kwargs['stderr_filter']

    @property
    def stdout_filter(self) -> typing.Optional[logging.Filter]:
        """
        A filter used when logging the stdout stream with the subprocess.
        """
        return self._stdout_filter

    @stdout_filter.setter
    def stdout_filter(self, filter: typing.Optional[logging.Filter]) -> None:
        self._stdout_filter = filter

    @property
    def stderr_filter(self) -> typing.Optional[logging.Filter]:
        """
        A filter used when logging the stderr stream with the subprocess.
        """
        return self._stderr_filter

    @stderr_filter.setter
    def stderr_filter(self, filter: typing.Optional[logging.Filter]) -> None:
        self._stderr_filter = filter

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--cwd', help='The working directory to launch the subprocess at.')
        arguments.add_argument('--logfile', help='Path to a file to write stdout, stderr, and test logs to.')
        arguments.add_argument('--logfile-amend',
                               default=False,
                               help=textwrap.dedent('''
                               If True then the logfile will be amended otherwise it will be overwritten
                               (the default)
                               ''').strip())
        arguments.add_argument('--logfile-format',
                               default='%(asctime)s %(levelname)s %(name)s: %(message)s',
                               help='Logger format to use for the logfile.')
        arguments.add_argument('--logfile-date-format',
                               default='%Y-%m-%d %H:%M:%S',
                               help='Logger date format to use for the logfile.')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        """
        +--------------+---------------------------+-------------------------------------------------------------------+
        | **Artifacts**                                                                                                |
        |                                                                                                              |
        +--------------+---------------------------+-------------------------------------------------------------------+
        | key          | type                      | Notes                                                             |
        +==============+===========================+===================================================================+
        | ``cmd``      | str                       | The command used to execute the subprocess.                       |
        +--------------+---------------------------+-------------------------------------------------------------------+
        | ``logfile``  | Optional[pathlib.Path]    | A file containing stdout, stderr, and test logs                   |
        +--------------+---------------------------+-------------------------------------------------------------------+
        """
        artifacts = nanaimo.Artifacts()

        cmd = self.on_construct_command(args, artifacts)
        setattr(artifacts, 'cmd', cmd)

        logfile_handler = None  # type: typing.Optional[logging.FileHandler]

        logfile = self.get_arg_covariant(args, 'logfile')
        logfile_amend = bool(self.get_arg_covariant(args, 'logfile-amend'))
        logfile_fmt = self.get_arg_covariant(args, 'logfile-format')
        logfile_datefmt = self.get_arg_covariant(args, 'logfile-date-format')

        cwd = self.get_arg_covariant(args, 'cwd')

        if logfile is not None:
            setattr(artifacts, 'logfile', logfile)
            logfile_handler = logging.FileHandler(filename=str(logfile), mode=('a' if logfile_amend else 'w'))
            file_formatter = logging.Formatter(fmt=logfile_fmt, datefmt=logfile_datefmt)
            logfile_handler.setFormatter(file_formatter)
            self._logger.addHandler(logfile_handler)

        stdout_filter = self._stdout_filter
        stderr_filter = self._stderr_filter

        if stdout_filter is not None:
            self._logger.addFilter(stdout_filter)
        if stderr_filter is not None:
            self._logger.addFilter(stderr_filter)

        try:
            self._logger.debug('About to execute command "%s" in a subprocess shell', cmd)

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )  # type: asyncio.subprocess.Process

            # Simply let the background process do it's thing and wait for it to finish.
            await self._wait_for_either_until_neither(
                (proc.stdout if proc.stdout is not None else self._NoopStreamReader()),
                (proc.stderr if proc.stderr is not None else self._NoopStreamReader()))

            await proc.wait()

            self._logger.debug('command "%s" exited with %i', cmd, proc.returncode)

            artifacts.result_code = proc.returncode
            return artifacts
        finally:
            if stderr_filter is not None:
                self._logger.removeFilter(stderr_filter)
            if stdout_filter is not None:
                self._logger.removeFilter(stdout_filter)
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
                                             stderr: asyncio.StreamReader) -> None:
        """
        Wait for a line of data from either stdout or stderr and log this data as received.
        When both are EOF then exit.

        :returns: Tuple of stdout, stderr
        """
        future_out = asyncio.ensure_future(stdout.readline())
        future_err = asyncio.ensure_future(stderr.readline())

        pending = set([future_out, future_err])  # type: typing.Set[asyncio.Future]
        done = set()  # type: typing.Set[asyncio.Future]

        while len(pending) > 0:

            done, pending = await asyncio.wait(pending)

            for future_done in done:
                result = future_done.result()
                if len(result) > 0:
                    line = result.decode(errors='replace')
                    if future_done == future_err:
                        future_err = asyncio.ensure_future(stderr.readline())
                        pending.add(future_err)
                        self._logger.error(self._ensure_no_newline_at_end(line))
                    else:
                        future_out = asyncio.ensure_future(stdout.readline())
                        pending.add(future_out)
                        self._logger.info(self._ensure_no_newline_at_end(line))
                elif future_done == future_err and not stderr.at_eof():
                    # spurious awake?
                    future_err = asyncio.ensure_future(stderr.readline())
                    pending.add(future_err)
                elif future_done == future_out and not stdout.at_eof():
                    # spurious awake?
                    future_out = asyncio.ensure_future(stdout.readline())
                    pending.add(future_out)

    @staticmethod
    def _ensure_no_newline_at_end(text: str) -> str:
        if text.endswith('\n'):
            text = text[:-1]
        if text.endswith('\r'):
            text = text[:-1]
        return text


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
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.get_event_loop()
        return self._loop

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


class PluggyFixtureManager:
    """
    DEPRECATED. Do not use.
    """

    @staticmethod
    def type_factory(type_getter: typing.Callable[[], typing.Type['nanaimo.fixtures.Fixture']]) \
            -> typing.Callable[[], typing.Type['nanaimo.fixtures.Fixture']]:
        raise DeprecationWarning('DEPRECATED: do not use the PluggyFixtureManager.type_factory annotation anymore.'
                                 'Remove this annotation from your get_fixture_type method and change the name of '
                                 'this hook to "pytest_nanaimo_fixture_type".')

    def __init__(self):
        raise DeprecationWarning('PluggyFixtureManager has been removed. See '
                                 'nanaimo.pytest.plugin.PytestFixtureManager for replacement.')
