#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import nanaimo
import nanaimo.version


def test_arg_version(run_nait) -> None:  # type: ignore
    """
    Verify --version argument contract.
    """
    expected = nanaimo.version.__version__
    assert run_nait(['--version']).stdout.decode('utf-8').startswith(expected)


def test_help(run_nait) -> None:  # type: ignore
    """
    Verify --help doesn't explode.
    """
    result = run_nait(['jlink', '--help']).stdout.decode('utf-8')
    assert len(result) > 4
    print(result)


def test_nanaimo_bar(run_nait) -> None:  # type: ignore
    """
    Eat your dessert!
    """
    result = run_nait(['--log-cli-level', 'DEBUG', 'nanaimo_bar']).stdout.decode('utf-8')
    print(result)


def test_environ(run_nait) -> None:  # type: ignore
    """
    Validate the environment duplication logic.
    """
    result = run_nait(['--environ-shell', '--environ', 'foo=bar']).stdout.decode('utf-8')
    assert result.find('export NANAIMO_UNITTEST="This is a nanaimo unittest environment."') != -1
    assert result.find('export foo="bar"') != -1
