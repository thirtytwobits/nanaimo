#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import os
import pathlib
import subprocess
import typing

import pytest

import fixtures
import nanaimo
from nanaimo.config import ArgumentDefaults


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
    return fixtures.Paths(request.module.__file__)


@pytest.fixture
def test_config(request):  # type: ignore
    return pathlib.Path(fixtures.__file__).parent / pathlib.Path('test').with_suffix('.cfg')


@pytest.fixture
def local_setup_cfg(request):  # type: ignore
    return pathlib.Path(fixtures.__file__).parent.parent.parent / pathlib.Path('setup').with_suffix('.cfg')


@pytest.fixture
def nanaimo_defaults(request):  # type: ignore
    return ArgumentDefaults(pathlib.Path(fixtures.__file__).parent / pathlib.Path('test').with_suffix('.cfg'))


@pytest.fixture
def dummy_nanaimo_fixture(request):  # type: ignore
    return fixtures.DummyFixture(nanaimo.FixtureManager())


@pytest.fixture
def mock_JLinkExe(request):  # type: ignore
    return pathlib.Path(fixtures.__file__).parent / pathlib.Path('mock_JLinkExe').with_suffix('.py')


@pytest.fixture
def s32K144_jlink_script(request):  # type: ignore
    jlink_file = pathlib.Path('test_math_saturation_loadfile_swd').with_suffix('.jlink')
    return pathlib.Path(fixtures.__file__).parent / jlink_file


@pytest.fixture
def s32K144_jlink_scripts(request):  # type: ignore
    return pathlib.Path(fixtures.__file__).parent.glob('*.jlink')
