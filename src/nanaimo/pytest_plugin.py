#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import nanaimo
import typing
import pluggy


class _PyTestArguments(nanaimo.Arguments):

    def __init__(self, testparser):  # type: ignore
        self._testparser = testparser

    def add_argument(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._testparser.addoption(*args, **kwargs)

    def set_defaults(self, **kwargs: typing.Any) -> None:
        raise NotImplementedError('pytest plugin does not support setting defaults.')


def pytest_addoption(parser) -> None:  # type: ignore
    pytest_pm = pluggy.PluginManager('pytest')
    fixture_types = nanaimo.Fixture.get_plugin_manager().hook.get_fixture_type()
    for fixture_type in fixture_types:
        group = parser.getgroup(fixture_type.__name__)
        args = _PyTestArguments(group)
        fixture_type.on_visit_test_arguments(args)
        pytest_pm.register(fixture_type, type(fixture_type).__name__)
