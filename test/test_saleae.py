#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import pytest

import nanaimo
import nanaimo.fixtures


@pytest.mark.asyncio
async def test_saleae_exists(nanaimo_bar: nanaimo.fixtures.Fixture) -> None:
    """
    Just making sure the fixture exists. More when issue #16 is completed.
    """
    assert nanaimo_bar.get_canonical_name() is not None
