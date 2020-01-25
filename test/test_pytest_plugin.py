#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import pytest

import nanaimo
import nanaimo.fixtures
from nanaimo.pytest.plugin import assert_success


@pytest.mark.asyncio
async def test_jlink_plugin(nanaimo_jlink_upload: nanaimo.fixtures.Fixture) -> None:
    """
    Make sure we've properly exported jlink as a pytest plugin.
    """
    assert isinstance(nanaimo_jlink_upload, nanaimo.fixtures.Fixture)


@pytest.mark.asyncio
async def test_nanaimo_bar(nanaimo_bar: nanaimo.fixtures.Fixture) -> None:
    """
    Test eating a Nanaimo bar (exercises directly exposing a plugin to pytest.)
    """
    assert nanaimo_bar is not None
    assert 'nanaimo_bar' == nanaimo_bar.name
    artifacts = await nanaimo_bar.gather()
    assert artifacts is not None
    artifacts.eat()
    assert nanaimo_bar.loop.is_running()


@pytest.mark.asyncio
async def test_another_nanaimo_bar(nanaimo_fixture_manager: nanaimo.fixtures.FixtureManager) -> None:
    """
    Test eating another Nanaimo bar (exercises using fixtures across multiple tests)
    """
    nanaimo_bar = nanaimo_fixture_manager.create_fixture('nanaimo_bar')
    assert nanaimo_bar is not None
    assert 'nanaimo_bar' == nanaimo_bar.name
    artifacts = await nanaimo_bar.gather()
    assert artifacts is not None
    artifacts.eat()
    assert nanaimo_bar.loop.is_running()


@pytest.mark.xfail
def test_assert_success() -> None:
    nanaimo.pytest.plugin.assert_success(nanaimo.Artifacts(1))


@pytest.mark.asyncio
async def test_plugin_from_conftest(nanaimo_bar_from_conftest: nanaimo.fixtures.Fixture) -> None:
    assert_success(await nanaimo_bar_from_conftest.gather())
