#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
Built-in :class:`NanaimoTest` for common scenarios.
"""
import asyncio
import pathlib

import nanaimo
import nanaimo.serial
import nanaimo.instruments
import nanaimo.instruments.jlink


class GTestOverJLink(nanaimo.NanaimoTest):

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        nanaimo.serial.AbstractSerial.on_visit_test_arguments(arguments)
        nanaimo.instruments.jlink.ProgramUploaderJLink.on_visit_test_arguments(arguments)

    async def __call__(self, args: nanaimo.Namespace) -> int:
        import nanaimo
        import nanaimo.serial
        import nanaimo.parsers.gtest
        import nanaimo.instruments.jlink

        uploader = nanaimo.instruments.jlink.ProgramUploaderJLink()
        jlink_scripts = pathlib.Path(args.base_path).glob(args.jlink_scripts)
        parser = nanaimo.parsers.gtest.Parser(args.test_timeout_seconds)

        result = 0
        with nanaimo.serial.ConcurrentUart.new_default(args.port, args.port_speed) as monitor:
            for script in jlink_scripts:
                if result != 0:
                    break
                result = await asyncio.wait_for(uploader.upload(script), timeout=args.upload_timeout_seconds)
                if result != 0:
                    break
                result = await parser.read_test(monitor)

        return result
