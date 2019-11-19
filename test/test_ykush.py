#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import nanaimo
import nanaimo.fixtures


def test_ykush_exists(nanaimo_instr_ykush: nanaimo.fixtures.Fixture) -> None:
    """
    Just making sure the fixture exists.
    """
    assert nanaimo_instr_ykush.get_canonical_name() is not None
