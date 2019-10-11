#!/usr/bin/env python3
#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import sys
from typing import Dict

import setuptools

if int(setuptools.__version__.split('.')[0]) < 30:
    print('A newer version of setuptools is required. The current version does not support declarative config.',
          file=sys.stderr)
    sys.exit(1)

version = {}  # type: Dict
with open('src/nanaimo/version.py') as fp:
    exec(fp.read(), version)

setuptools.setup(version=version['__version__'])
