#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
Nanaimo is composed of three primary object types:

    1. :class:`Fixture` – A fixture
    2. :class:`Instrument` – An Instrument
    3. :class:`Activity` – An activity

.. figure:: https://thirtytwobits.github.io/nanaimo/images/static_state_1.png
   :alt: Static-state diagram of Nanaimo's primary types.

   Static-state diagram of Nanaimo's primary types.

.. figure:: https://thirtytwobits.github.io/nanaimo/images/object_1.png
   :alt: Object example of Nanaimo's primary types in use.

   Object example of Nanaimo's primary types in use.

"""
import abc
import logging
import asyncio
import typing
import math


class AssertionError(RuntimeError):
    """
    Thrown by Nanaimo tests when an assertion has failed.

    .. Note::
        This exception should be used only when the state of a :class:`Fixture`
        was invalid. You should use pytest tests and assertions when writing validation
        cases for fixture output like log files or sensor data.
    """
    pass


class Arguments(metaclass=abc.ABCMeta):
    """
    Protocol for argument type that supports both argparse and pytest arguments concepts.

    .. Note::
        This will go away at some disant point in the future where Nanaimo supports only
        Python 3.8 and newer since `PEP-544 protocols <https://www.python.org/dev/peps/pep-0544/>`_
        can be used.
    """
    @abc.abstractmethod
    def add_argument(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        ...

    @abc.abstractmethod
    def set_defaults(self, **kwargs: typing.Any) -> None:
        ...


class Namespace:
    """
    Generic object that acts like :class:`argparse.Namespace` but can be created using pytest
    plugin arguments as well.
    """
    def __init__(self, parent: typing.Any):
        for name in vars(parent):
            setattr(self, name, getattr(parent, name))

    def __getattr__(self, key: str) -> typing.Any:
        return self.__dict__[key]

    def __eq__(self, other: typing.Any) -> bool:
        return vars(self) == vars(other)

    def __contains__(self, key: str) -> typing.Any:
        return key in self.__dict__


class Fixture(metaclass=abc.ABCMeta):
    """
    Common, abstract class for pytest fixtures based on Nanaimo. Nanaimo fixtures provide a visitor pattern for arguments that
    are common for both pytest extra arguments and for argparse commandline arguments. This allows a Nanaimo fixture to expose
    a direct invocation mode for debuging with the same arguments used by the fixture as a pytest plugin.

    .. code-block:: python

        import nanaimo
        class MyFixture(nanaimo.Fixture):
            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                arguments.add_argument('--foo', default='bar')

    `MyFixture` can now be used from a commandline like::

        python -m nanaimo MyFixture --foo baz

    or as part of a pytest::

        pytest --foo=baz

    """

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """
        The asyncio EventLoop in use by this Fixture.
        """
        return self._loop

    @classmethod
    @abc.abstractmethod
    def on_visit_test_arguments(cls, arguments: Arguments) -> None:
        ...

    @abc.abstractmethod
    async def __call__(self, args: Namespace) -> int:
        ...

    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop] = None):
        self._logger = logging.getLogger(type(self).__name__)
        self._loop = (loop if loop is not None else asyncio.get_event_loop())

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
                                            *args: typing.Union[typing.Coroutine, asyncio.Future]) -> typing.Set[asyncio.Future]:
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

        start_time = self._loop.time()
        wait_timeout = (timeout_seconds if timeout_seconds > 0 else None)

        while True:
            done, pending = await asyncio.wait(
                the_children_are_our_futures,
                timeout=wait_timeout,
                return_when=asyncio.FIRST_COMPLETED)

            if observing_my_future.done():
                return done, pending

            if wait_timeout is not None and self._loop.time() - start_time > wait_timeout:
                break

        raise asyncio.TimeoutError()
