#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import nanaimo


class CanonicallyNamed(nanaimo.Fixture):

    fixture_name = 'foo_bar'


def test_canonical_name(dummy_nanaimo_fixture: nanaimo.Fixture) -> None:
    """
    Verify the behavior of Fixture.get_canonical_name()
    """
    assert 'fixtures.DummyFixture' == type(dummy_nanaimo_fixture).get_canonical_name()
    assert CanonicallyNamed.fixture_name == CanonicallyNamed.get_canonical_name()
