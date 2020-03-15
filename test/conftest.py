#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import asyncio
import os
import pathlib
import subprocess
import typing

import pytest

import material
import material.simulators
import nanaimo
import nanaimo.config
import nanaimo.fixtures


@pytest.fixture
def run_nait(request):  # type: ignore
    def _run_nait(args: typing.List[str],
                  check_result: bool = True,
                  env: typing.Optional[typing.Dict[str, str]] = None) -> subprocess.CompletedProcess:
        """
        Helper to invoke nait for unit testing within the proper python coverage wrapper.
        """
        root_dir = pathlib.Path(request.module.__file__).parent.parent
        setup = root_dir / pathlib.Path('setup').with_suffix('.cfg')
        coverage_args = ['coverage', 'run', '--parallel-mode', '--rcfile={}'.format(str(setup))]
        nait = ['-m', 'nanaimo']
        this_env = os.environ.copy()
        if env is not None:
            this_env.update(env)
        return subprocess.run(coverage_args + nait + args,
                              check=check_result,
                              stdout=subprocess.PIPE,
                              env=this_env)
    return _run_nait


@pytest.fixture
def paths_for_test(request):  # type: ignore
    return material.Paths(request.module.__file__)


@pytest.fixture
def test_config(request):  # type: ignore
    return pathlib.Path(material.__file__).parent / pathlib.Path('test').with_suffix('.cfg')


@pytest.fixture
def local_setup_cfg(request):  # type: ignore
    return pathlib.Path(material.__file__).parent.parent.parent / pathlib.Path('setup').with_suffix('.cfg')


@pytest.fixture
def nanaimo_defaults(request):  # type: ignore
    test_cfg = pathlib.Path(material.__file__).parent / pathlib.Path('test').with_suffix('.cfg')
    return nanaimo.config.ArgumentDefaults(test_cfg)


@pytest.fixture
def dummy_nanaimo_fixture(request):  # type: ignore
    return material.DummyFixture(nanaimo.fixtures.FixtureManager())


@pytest.fixture
def mock_JLinkExe(request):  # type: ignore
    return pathlib.Path(material.__file__).parent / pathlib.Path('mock_JLinkExe').with_suffix('.py')


@pytest.fixture
def test_build_config_hex(request):  # type: ignore
    return pathlib.Path(material.__file__).parent / pathlib.Path('test_build_config').with_suffix('.hex')


@pytest.fixture
def test_jlink_template(request):  # type: ignore
    return pathlib.Path(material.__file__).parent / pathlib.Path('test').with_suffix('.jlink')


@pytest.fixture
def serial_simulator_type(request):  # type: ignore
    return material.simulators.Serial


@pytest.fixture
def build_output(request):  # type: ignore
    builddir = pathlib.Path(material.__file__).parent.parent.parent / pathlib.Path('build')
    if not builddir.exists():
        builddir.mkdir()
    return builddir


@pytest.fixture
def nanaimo_bar_from_conftest(nanaimo_fixture_manager, nanaimo_arguments) -> 'nanaimo.fixtures.Fixture':
    return nanaimo.builtin.nanaimo_bar.Fixture(nanaimo_fixture_manager, nanaimo_arguments)
