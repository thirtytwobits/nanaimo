#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import pathlib
import typing
import asyncio


class LogFile:

    def __init__(self, log_file: pathlib.Path, loop: typing.Optional[asyncio.AbstractEventLoop] = None):
        self._loop = (loop if loop is not None else asyncio.get_event_loop())
        self._log_file = log_file
        self._tail = True

    def cancel_tail(self) -> None:
        self._tail = False

    async def tail(self) -> typing.AsyncGenerator[str, None]:
        self._tail = True
        with open(str(self._log_file), 'r') as log_file:
            while self._tail:
                line = await self._loop.run_in_executor(None, log_file.readline)
                if line:
                    yield line
