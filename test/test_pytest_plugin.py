#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import pytest

import nanaimo


def test_nanaimo_fixture_manager(nanaimo_fixture_manager: nanaimo.FixtureManager) -> None:
    """
    Ensure the fixture manager ... er; fixture works as expected.
    """
    assert type(nanaimo_fixture_manager) == nanaimo.PluggyFixtureManager
    gtest_fixture = nanaimo_fixture_manager.create_fixture('gtest_over_jlink', nanaimo.Namespace())
    assert isinstance(gtest_fixture, nanaimo.Fixture)


@pytest.mark.asyncio
async def test_gtest_over_jlink_plugin(gtest_over_jlink: nanaimo.Fixture) -> None:
    """
    Make sure we've properly exported gtest_over_jlink as a pytest plugin.
    """
    assert isinstance(gtest_over_jlink, nanaimo.Fixture)


@pytest.mark.asyncio
async def test_nanaimo_bar(nanaimo_bar: nanaimo.Fixture) -> None:
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
async def test_another_nanaimo_bar(nanaimo_fixture_manager: nanaimo.FixtureManager) -> None:
    """
    Test eating another Nanaimo bar (exercises using fixtures across multiple tests)
    """
    nanaimo_bar = nanaimo_fixture_manager.get_fixture('nanaimo_bar')
    assert nanaimo_bar is not None
    assert 'nanaimo_bar' == nanaimo_bar.name
    artifacts = await nanaimo_bar.gather()
    assert artifacts is not None
    artifacts.eat()
    assert nanaimo_bar.loop.is_running()
