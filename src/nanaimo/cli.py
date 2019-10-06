#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import argparse
import asyncio
import logging
import sys
import typing

import nanaimo


class _ArgparseSubparserArguments(nanaimo.Arguments):
    """
    Nanaimo :class:`Arguments` that delegates to a wrapped
    :class:`argparse.ArgumentParser` instance.
    """

    @classmethod
    def visit_argparse(cls,
                       test_class: typing.Type['nanaimo.Fixture'],
                       subparsers: argparse._SubParsersAction,
                       loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> None:
        subparser = subparsers.add_parser(test_class.__name__)  # type: 'argparse.ArgumentParser'
        subparser.add_argument('--test-timeout-seconds',
                               default='30',
                               type=float,
                               help='''Test will be killed and marked as a failure after
waiting for a result for this amount of time.''')
        test_class.on_visit_test_arguments(cls(subparser))
        subparser.set_defaults(func=test_class(loop))

    def __init__(self, subparser: argparse.ArgumentParser):
        self._subparser = subparser

    def add_argument(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._subparser.add_argument(*args, **kwargs)

    def set_defaults(self, **kwargs: typing.Any) -> None:
        self._subparser.set_defaults(**kwargs)


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

    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('--verbose', '-v', action='count',
                        help='verbosity level (-v, -vv)')

    subparsers = parser.add_subparsers(help='sub-command help')

    import nanaimo.builtin  # noqa: F401

    for test in nanaimo.Fixture.__subclasses__():
        # https://github.com/python/mypy/issues/5374
        _ArgparseSubparserArguments.visit_argparse(test, subparsers, loop)  # type: ignore

    return parser


def _setup_logging(args: argparse.Namespace) -> None:
    fmt = '%(name)s : %(message)s'
    level = {0: logging.WARNING, 1: logging.INFO,
             2: logging.DEBUG}.get(args.verbose or 0, logging.DEBUG)
    logging.basicConfig(stream=sys.stderr, level=level, format=fmt)
    if args.verbose is not None and args.verbose >= 3:
        logging.getLogger('asyncio').setLevel(logging.DEBUG)


def main() -> int:
    """
    CLI entrypoint for running Nanaimo tests.
    """

    loop = asyncio.get_event_loop()

    parser = _make_parser(loop)
    args = parser.parse_args()

    _setup_logging(args)

    if hasattr(args, 'func'):
        result = loop.run_until_complete(args.func(nanaimo.Namespace(args)))
        try:
            return int(result)
        except ValueError:
            print('Nanaimo tests must return an int result!')
            raise
    else:
        parser.print_usage()
        return -1
