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
