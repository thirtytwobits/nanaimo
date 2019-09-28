#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#


def test_test_hardware_fixture(testdir) -> None:  # type: ignore
    testdir.makeconftest(
        """
# pytest_plugins = "nanaimo.pytest_plugin"
""")
    testdir.makepyfile("""
def test_hardware_fixture(hardware):
    assert hardware() == "Hello Pytest"
""")

    # run all tests with pytest
    result = testdir.runpytest()

    # check that all 4 tests passed
    result.assert_outcomes(passed=1)
