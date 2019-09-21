#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import asyncio
import logging
import re
import time
import nanaimo.serial


class Parser:
    """
    Uses a given monitor to watch for google test results.
    """

    def __init__(self, timeout_seconds: float):
        self._logger = logging.getLogger(__name__)
        self._timeout_seconds = timeout_seconds
        self._completion_pattern = re.compile(r'\[\s*(PASSED|FAILED)\s*\]\s*(\d+)\s+tests?\.')

    async def read_test(self, uart: nanaimo.serial.ConcurrentUartMonitor) -> int:
        start_time = time.monotonic()
        result = 1
        line_count = 0
        while True:
            if time.monotonic() - start_time > self._timeout_seconds:
                result = 2
                self._logger.warning('gtest.Parser timeout after %f seconds', time.monotonic() - start_time)
                break
            line = uart.readline()
            if line is None:
                await asyncio.sleep(.250)
                continue

            self._logger.debug(line)
            line_count += 1
            line_match = self._completion_pattern.match(line)
            if line_match is not None:
                result = (0 if line_match.group(1) == 'PASSED' else 1)
                break
        if 0 == result:
            self._logger.info('Detected successful test after %f seconds.', time.monotonic() - start_time)
        self._logger.debug('Processed %d lines. There were %d buffer full events reported.', line_count, uart.buffer_full_events)
        return result
