#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
Built-in :class:`NanaimoTest` for common scenarios.
"""
import argparse
import asyncio
import pathlib

import nanaimo
import nanaimo.serial
import nanaimo.jlink


class GTestOverJLink(nanaimo.NanaimoTest):

    @classmethod
    def on_visit_argparse_subparser(cls, subparsers: argparse._SubParsersAction, subparser: argparse.ArgumentParser) -> None:
        nanaimo.serial.AbstractSerial.on_visit_argparse_subparser(subparsers, subparser)
        nanaimo.jlink.ProgramUploaderJLink.on_visit_argparse_subparser(subparsers, subparser)

    async def __call__(self, args: argparse.Namespace) -> int:
        import nanaimo
        import nanaimo.serial
        import nanaimo.gtest
        import nanaimo.jlink

        uploader = nanaimo.jlink.ProgramUploaderJLink()
        jlink_scripts = pathlib.Path(args.base_path).glob(args.jlink_scripts)
        parser = nanaimo.gtest.Parser(args.test_timeout_seconds)

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
