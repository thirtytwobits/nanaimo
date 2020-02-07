#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import argparse
import asyncio
import pathlib
import typing

import pytest

import nanaimo
import nanaimo.builtin
import nanaimo.fixtures
from nanaimo import assert_success
from nanaimo.builtin import nanaimo_bar, nanaimo_cmd, nanaimo_gather


class CanonicallyNamed(nanaimo.fixtures.Fixture):

    fixture_name = 'foo_bar'


def test_canonical_name(dummy_nanaimo_fixture: nanaimo.fixtures.Fixture) -> None:
    """
    Verify the behavior of Fixture.get_canonical_name()
    """
    assert 'material.DummyFixture' == type(dummy_nanaimo_fixture).get_canonical_name()
    assert CanonicallyNamed.fixture_name == CanonicallyNamed.get_canonical_name()


@pytest.mark.asyncio
async def test_gather_coroutines(nanaimo_fixture_manager: nanaimo.fixtures.FixtureManager) -> None:

    parser = argparse.ArgumentParser()
    nanaimo_gather.Fixture.on_visit_test_arguments(nanaimo.Arguments(parser, required_prefix='gather'))
    args = nanaimo.Namespace(parser.parse_args(['--gather-coroutine', 'nanaimo_bar',
                                                '--gather-coroutine', 'nanaimo_bar']))

    gather_fixture = nanaimo_gather.Fixture(nanaimo_fixture_manager, args)

    results = await gather_fixture.gather()

    assert results.result_code == 0


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks(dummy_nanaimo_fixture: nanaimo.fixtures.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture
    """

    async def evaluating() -> int:
        return 0

    async def running() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    result = await dummy_nanaimo_fixture.observe_tasks_assert_not_done(evaluating(),
                                                                       None,
                                                                       running())
    assert len(result) == 1
    should_be_running = result.pop()

    assert not should_be_running.done()

    assert 1 == await should_be_running


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks_failure(dummy_nanaimo_fixture: nanaimo.fixtures.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks exit.
    """

    async def evaluating() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    async def running() -> int:
        return 1

    with pytest.raises(nanaimo.AssertionError):
        await dummy_nanaimo_fixture.observe_tasks_assert_not_done(evaluating(),
                                                                  None,
                                                                  running())


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks_failure_no_assert(dummy_nanaimo_fixture: nanaimo.fixtures.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks exit but without throwing
    an assertion error.
    """

    async def evaluating() -> int:
        waits = 2
        while waits > 0:
            await asyncio.sleep(.1)
            waits -= 1
        return 1

    async def running() -> int:
        return 1

    result = await dummy_nanaimo_fixture.observe_tasks(evaluating(),
                                                       None,
                                                       running())

    assert 0 == len(result)


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_observe_tasks_timeout(dummy_nanaimo_fixture: nanaimo.fixtures.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks do not exit.
    """

    async def evaluating() -> int:
        while True:
            await asyncio.sleep(1)

    async def running() -> int:
        while True:
            await asyncio.sleep(1)

    with pytest.raises(asyncio.TimeoutError):
        await dummy_nanaimo_fixture.observe_tasks_assert_not_done(evaluating(),
                                                                  1,
                                                                  running())


@pytest.mark.timeout(20)
@pytest.mark.asyncio
async def test_countdown_sleep(dummy_nanaimo_fixture: nanaimo.fixtures.Fixture) -> None:
    """
    Test the observe_tasks method of Fixture where the running tasks do not exit.
    """
    await dummy_nanaimo_fixture.countdown_sleep(5.3)


@pytest.mark.timeout(20)
@pytest.mark.asyncio
async def test_gather_timeout(gather_timeout_fixture: nanaimo.fixtures.Fixture) -> None:
    """
    Test the standard fixture timeout.
    """
    gather_timeout_fixture.gather_timeout_seconds = 1.0
    with pytest.raises(asyncio.TimeoutError):
        await gather_timeout_fixture.gather()


@pytest.mark.asyncio
async def test_subprocess_fixture_logfile(build_output: pathlib.Path) -> None:
    """
    Verify the subprocess fixture base class properly creates a logfile.
    """
    import nanaimo.version

    logfile = build_output / pathlib.Path('test_subprocess_fixture_logfile').with_suffix('.log')
    class SubprocessTestHarness(nanaimo.fixtures.SubprocessFixture):

        argument_prefix = 'test-subprocess-fixture'

        @classmethod
        def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
            super().on_visit_test_arguments(arguments)

        def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
            return 'nait --version'

    subject = SubprocessTestHarness(nanaimo.fixtures.FixtureManager())
    artifacts = await subject.gather(
        test_subprocess_fixture_logfile=str(logfile),
        test_subprocess_fixture_logfile_amend=False
    )

    assert artifacts.result_code == 0

    found = False
    with open(str(artifacts.logfile), 'r') as logfile_io:
        for line in logfile_io:
            print(line)
            if line.find(nanaimo.version.__version__) != -1:
                found = True
                break

    assert found


@pytest.mark.asyncio
async def test_subprocess_fixture_environment(build_output: pathlib.Path) -> None:
    """
    Verify that the subprocess environment is populated from configuration.
    """
    class SubprocessTestHarness(nanaimo.fixtures.SubprocessFixture):

        @classmethod
        def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
            super().on_visit_test_arguments(arguments)

        def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
            # NANAIMO_UNITTEST is set in our setup.cfg
            return 'echo ${NANAIMO_UNITTEST}'

    subject = SubprocessTestHarness(nanaimo.fixtures.FixtureManager())
    filter = nanaimo.fixtures.SubprocessFixture.SubprocessMessageAccumulator()
    subject.stdout_filter = filter

    artifacts = await subject.gather()

    assert artifacts.result_code == 0

    defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()

    nanaimo_environ = nanaimo.config.ArgumentDefaults.as_dict(defaults['environ'])
    assert 'NANAIMO_UNITTEST' in nanaimo_environ
    assert nanaimo_environ['NANAIMO_UNITTEST'] == filter.getvalue()


@pytest.mark.asyncio
@pytest.mark.skip(reason='https://github.com/thirtytwobits/nanaimo/issues/84')
async def test_composite_fixture(event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Test creation of a composite fixture.
    """

    class Composite(nanaimo_bar.Fixture, nanaimo_cmd.Fixture):

        fixture_name = 'test_composite_fixture'
        argument_prefix = 'tcf'

        def __init__(self, manager: nanaimo.fixtures.FixtureManager,
                     args: nanaimo.Namespace,
                     **kwargs: typing.Any) -> None:
            nanaimo_bar.Fixture.__init__(self, manager, args, **kwargs)
            nanaimo_cmd.Fixture.__init__(self, manager, args, **kwargs)
            self._gather = nanaimo_gather.Fixture(manager, args, **kwargs)

        @classmethod
        def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
            nanaimo_bar.Fixture.visit_test_arguments(arguments)
            nanaimo_cmd.Fixture.visit_test_arguments(arguments)

        async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
            coroutines = [
                nanaimo_bar.Fixture.on_gather(self, args),
                nanaimo_cmd.Fixture.on_gather(self, args)
            ]
            return await self._gather.gather(gather_coroutine=coroutines)

    composite = Composite(nanaimo.fixtures.FixtureManager(event_loop),
                          nanaimo.Namespace())

    filter = nanaimo.fixtures.SubprocessFixture.SubprocessMessageAccumulator()
    composite.stdout_filter = filter

    results = await composite.gather(tcf_shell='nait --version')

    results.eat()
    assert filter.getvalue() == nanaimo.version.__version__


@pytest.mark.asyncio
async def test_subprocess_read_illegal_encoding(paths_for_test: typing.Any) -> None:
    """
    Verify the subprocess fixture base class can handle unknown input without 'sploding.
    """
    import nanaimo.version

    class SubprocessTestHarness(nanaimo.fixtures.SubprocessFixture):

        argument_prefix = 'test-subprocess-fixture'

        @classmethod
        def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
            super().on_visit_test_arguments(arguments)

        def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
            return 'export PYTHONIOENCODING=utf_16_be && python {} {}'.format(
                str(paths_for_test.unicode_py), str(paths_for_test.unicode_big))

    stdout = nanaimo.fixtures.SubprocessFixture.SubprocessMessageAccumulator()
    stderr = nanaimo.fixtures.SubprocessFixture.SubprocessMessageAccumulator()
    subject = SubprocessTestHarness(nanaimo.fixtures.FixtureManager())
    subject.stdout_filter = stdout
    subject.stderr_filter = stderr
    assert_success(await subject.gather())
