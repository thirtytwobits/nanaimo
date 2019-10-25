#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import typing
import pathlib
import pytest
import subprocess
import os


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
