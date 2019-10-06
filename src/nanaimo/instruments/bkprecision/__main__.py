#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import nanaimo.version
import nanaimo.connections
import nanaimo.instruments.bkprecision
import asyncio
import argparse
import sys
import logging


def _make_parser() -> argparse.ArgumentParser:
    epilog = '''**Example Usage**::

    python -m nanaimo.instruments.bkprecision \\
        --port /dev/serial/by-id/usb_TTL232R_BLAH_port0 \\
        on

----
'''

    parser = argparse.ArgumentParser(
        description='Send one-shot commands to the bk-precision',
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--version', action='version', version=nanaimo.version.__version__)

    parser.add_argument('--verbose', '-v', action='count',
                        help='verbosity level (-v, -vv)')

    parser.add_argument('--local-echo', '-e', action='store_true',
                        help='Enable debug logging of sent commands. Use with -vv.')

    parser.add_argument('--port',
                        help='The port the BK Precision power supply is connected to.')

    parser.add_argument('--timeout-seconds', default=2.5,
                        help='fractional seconds to wait for an OK before marking the command as failed.')

    parser.add_argument('command', help='Command to send to the power supply.')
    return parser


args = _make_parser().parse_args()

#
# Setup Python logging.
#
fmt = '%(name)20s %(levelname)7s: %(message)s'
level = {0: logging.WARNING, 1: logging.INFO,
         2: logging.DEBUG}.get(args.verbose or 0, logging.DEBUG)
logging.basicConfig(stream=sys.stderr, level=level, format=fmt)

#
# Start asyncio loop (3.5 compatible version)
#
loop = asyncio.get_event_loop()

with nanaimo.connections.uart.ConcurrentUart.new_default(args.port, 9600, loop) as serial:
    serial.echo = args.local_echo
    bk = nanaimo.instruments.bkprecision.Series1900BUart(serial, args.timeout_seconds)
    result = loop.run_until_complete(bk.send_command(args.command))

sys.exit(result)
