#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import fixtures
import nanaimo
import os


def test_ugt_parser() -> None:
    serial = fixtures.MockSerial(fixtures.FAKE_TEST_0)
    last_line = fixtures.FAKE_TEST_0[-1]
    with nanaimo.ConcurrentUartMonitor(serial) as monitor:
        while True:
            line = monitor.readline()
            if line is None:
                os.sched_yield()
                continue
            print(line)
            if line == last_line:
                break
