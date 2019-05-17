#!/usr/bin/env python3
#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
    Fake jlink commander for unit testing.
"""
import sys
import argparse
import time


def main() -> int:

    parser = argparse.ArgumentParser(
        description='mock JLinkExe for unit testing')

    parser.add_argument('--simulate-error',
                        action='store_true',
                        help='Return non-zero from main.')

    parser.add_argument('-CommanderScript',
                        help='A Mock JLinkExe CommanderScript argument.')

    args = parser.parse_args()

    for i in range(0, 100):
        # act busy
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(.01)

    sys.stdout.write('\n')
    if args.simulate_error:
        sys.stdout.write('Simulating abnormal exit.\n')
        return 1
    else:
        sys.stdout.write('Simulating normal exit.\n')
        return 0


if __name__ == "__main__":
    sys.exit(main())
