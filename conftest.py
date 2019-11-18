#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
Enable pytest integration of doctests in source and/or in documentation.
"""

import fnmatch

from sybil import Sybil
from sybil.parsers.codeblock import CodeBlockParser
from sybil.parsers.doctest import DocTestParser

s = Sybil(
    parsers=[
        DocTestParser(),
        CodeBlockParser(),
    ],
    excludes=['test/fixtues/*'],
)


class _ReplacementSybilFilter:
    """
    Sybil's matcher isn't very good so we replace it with our own.
    """

    def __call__(self: Sybil, filename: str) -> bool:
        return fnmatch.fnmatch(filename, '*.rst') or fnmatch.fnmatch(filename, '*.py')


s.should_test_filename = _ReplacementSybilFilter()

pytest_collect_file = s.pytest()
