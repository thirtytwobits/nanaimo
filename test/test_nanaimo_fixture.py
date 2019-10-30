#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import nanaimo
import argparse
import nanaimo.builtin
from nanaimo.builtin import nanaimo_gather
import pytest


class CanonicallyNamed(nanaimo.Fixture):

    fixture_name = 'foo_bar'


def test_canonical_name(dummy_nanaimo_fixture: nanaimo.Fixture) -> None:
    """
    Verify the behavior of Fixture.get_canonical_name()
    """
    assert 'fixtures.DummyFixture' == type(dummy_nanaimo_fixture).get_canonical_name()
    assert CanonicallyNamed.fixture_name == CanonicallyNamed.get_canonical_name()


@pytest.mark.asyncio
async def test_gather_coroutines(nanaimo_fixture_manager: nanaimo.FixtureManager) -> None:

    parser = argparse.ArgumentParser()
    nanaimo_gather.Fixture.on_visit_test_arguments(nanaimo.Arguments(parser))
    args = nanaimo.Namespace(parser.parse_args(['--gather-coroutine', 'nanaimo_bar',
                                                '--gather-coroutine', 'nanaimo_bar']))

    gather_fixture = nanaimo_gather.Fixture(nanaimo_fixture_manager, args)

    results = await gather_fixture.gather()

    assert results.result_code == 0
