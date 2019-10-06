#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import nanaimo
import typing
import pytest


class _PyTestArguments(nanaimo.Arguments):

    def __init__(self, testparser):  # type: ignore
        self._testparser = testparser

    def add_argument(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._testparser.addoption(*args, **kwargs)

    def set_defaults(self, **kwargs: typing.Any) -> None:
        raise NotImplementedError('pytest plugin does not support setting defaults.')


def pytest_addoption(parser) -> None:  # type: ignore
    # import nanaimo.builtin  # noqa: F401

    # args = _PyTestArguments(parser)
    # for test in nanaimo.Fixture.__subclasses__():
    #     # https://github.com/python/mypy/issues/5374
    #     group = parser.getgroup(type(test).__name__)
    #     test.on_visit_test_arguments(args)
    pass


@pytest.fixture
def hardware(request) -> typing.Callable[[], str]:  # type: ignore
    # TODO: this is just a placeholder
    def _hello() -> str:
        return "Hello Pytest"

    return _hello
