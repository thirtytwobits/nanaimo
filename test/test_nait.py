#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import fixtures
import nanaimo
import nanaimo.version


def test_arg_version() -> None:
    """
    Verify --version argument contract.
    """
    expected = nanaimo.version.__version__
    assert fixtures.run_nait(['--version']).stdout.decode('utf-8').startswith(expected)


def test_help() -> None:
    """
    Verify --help doesn't explode.
    """
    result = fixtures.run_nait(['gtest_over_jlink', '--help']).stdout.decode('utf-8')
    assert len(result) > 4
    print(result)


def test_nanaimo_bar() -> None:
    """
    Eat your dessert!
    """
    result = fixtures.run_nait(['-vv', 'nanaimo_bar']).stdout.decode('utf-8')
    print(result)
