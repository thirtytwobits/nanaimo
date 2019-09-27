#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import abc
import argparse
import logging
import asyncio
import typing
import sys


class AssertionError(RuntimeError):
    """
    Thrown by Nanaimo tests when an assertion has failed.
    """
    pass


class NanaimoTest(metaclass=abc.ABCMeta):

    @classmethod
    def on_visit_argparse(cls, subparsers: argparse._SubParsersAction, loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> None:
        subparser = subparsers.add_parser(cls.__name__)  # type: 'argparse.ArgumentParser'
        subparser.add_argument('--test-timeout-seconds',
                               default='30',
                               type=float,
                               help='''Test will be killed and marked as a failure after
waiting for a result for this amount of time.''')
        cls.on_visit_argparse_subparser(subparsers, subparser)
        subparser.set_defaults(func=cls(loop))

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @classmethod
    @abc.abstractmethod
    def on_visit_argparse_subparser(cls, subparsers: argparse._SubParsersAction, subparser: argparse.ArgumentParser) -> None:
        ...

    @abc.abstractmethod
    async def __call__(self, args: argparse.Namespace) -> int:
        ...

    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop] = None):
        self._logger = logging.getLogger(type(self).__name__)
        self._loop = (loop if loop is not None else asyncio.get_event_loop())


def _make_parser(loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> argparse.ArgumentParser:
    """
        Defines the command-line interface. Provided as a separate factory method to
        support sphinx-argparse documentation.
    """

    epilog = '''**Example Usage**::

    python -m nanaimo -vv

----
'''

    parser = argparse.ArgumentParser(
        description='Run tests against hardware.',
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter)

    from nanaimo.version import __version__

    parser.add_argument('--version', action='version', version='.'.join(map(str, __version__)))

    parser.add_argument('--verbose', '-v', action='count',
                        help='verbosity level (-v, -vv)')

    subparsers = parser.add_subparsers(help='sub-command help')

    import nanaimo.builtin  # noqa: F401

    for test in NanaimoTest.__subclasses__():
        test.on_visit_argparse(subparsers, loop)

    return parser


def _setup_logging(args: argparse.Namespace) -> None:
    fmt = '%(name)s : %(message)s'
    level = {0: logging.WARNING, 1: logging.INFO,
             2: logging.DEBUG}.get(args.verbose or 0, logging.DEBUG)
    logging.basicConfig(stream=sys.stderr, level=level, format=fmt)


def main() -> int:
    """
    CLI entrypoint for running Nanaimo tests.
    """

    loop = asyncio.get_event_loop()

    parser = _make_parser(loop)
    args = parser.parse_args()

    _setup_logging(args)

    if hasattr(args, 'func'):
        result = loop.run_until_complete(args.func(args))
        try:
            return int(result)
        except ValueError:
            print('Nanaimo tests must return an int result!')
            raise
    else:
        parser.print_usage()
        return -1
