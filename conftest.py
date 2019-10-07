#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
Enable pytest integration of doctests in source and/or in documentation.
"""

from sybil import Sybil
from sybil.parsers.codeblock import CodeBlockParser
from sybil.parsers.doctest import DocTestParser

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(),
        CodeBlockParser(),
    ],
    pattern='*.py',
    excludes=['test/fixtues/*']
).pytest()
