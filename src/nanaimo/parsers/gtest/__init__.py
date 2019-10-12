#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
#                                       (@@@@%%%%%%%%%&@@&.
#                              /%&&%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%&@@(
#                              *@&%%%%%%%%%&&%%%%%%%%%%%%%%%%%%&&&%%%%%%%
#                               @   @@@(@@@@%%%%%%%%%%%%%%%%&@@&* @@@   .
#                               ,   .        .  .@@@&                   /
#                                .       .                              *
#                               @@              .                       @
#                              @&&&&&&@. .    .                     *@%&@
#                              &&&&&&&&&&&&&&&&@@        *@@############@
#                     *&/ @@ #&&&&&&&&&&&&&&&&&&&&@  ###################*
#                              @&&&&&&&&&&&&&&&&&&##################@
#                                 %@&&&&&&&&&&&&&&################@
#                                        @&&&&&&&&&&%#######&@%
#  nanaimo                                   (@&&&&####@@*
#
import asyncio
import logging
import re
import typing

import nanaimo.connections


class Parser:
    """
    Uses a given monitor to watch for google test results.
    """

    def __init__(self, timeout_seconds: float, loop: typing.Optional[asyncio.AbstractEventLoop] = None):
        self._loop = (loop if loop is not None else asyncio.get_event_loop())
        self._logger = logging.getLogger(__name__)
        self._timeout_seconds = timeout_seconds
        self._completion_pattern = re.compile(r'\[\s*(PASSED|FAILED)\s*\]\s*(\d+)\s+tests?\.')

    async def read_test(self, uart: nanaimo.connections.AbstractAsyncSerial) -> int:
        start_time = self._loop.time()
        result = 1
        line_count = 0
        while True:
            now = self._loop.time()
            if now - start_time > self._timeout_seconds:
                result = 2
                break
            try:
                line = await uart.get_line(timeout_seconds=self._timeout_seconds - (now - start_time))
            except asyncio.TimeoutError:
                result = 2
                break
            self._logger.debug(line)
            line_count += 1
            line_match = self._completion_pattern.match(line)
            if line_match is not None:
                result = (0 if line_match.group(1) == 'PASSED' else 1)
                break
        if 0 == result:
            self._logger.info('Detected successful test after %f seconds.', self._loop.time() - start_time)
        elif 2 == result:
            self._logger.warning('gtest.Parser timeout after %f seconds', self._loop.time() - start_time)
        self._logger.debug('Processed %d lines. There were %d buffer full events reported.',
                           line_count,
                           uart.rx_buffer_overflows)
        return result
