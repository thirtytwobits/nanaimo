#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
#                                       (@@@@%%%%%%%%%&@@&.
#                              /%&&%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%&@@(
#                              *@&%%%%%%%%%&&%%%%%%%%%%%%%%%%%%&&&%%%%%%%
#                               @   @@@(@@@@%%%%%%%%%%%%%%%%&@@&* @@@   .
#                               ,   .        .  .@@@&                   /
#                                .       .                              *
#                               @@              .                       @
#                              @&&&&&&@. .    .                     *@%&@
#                              &&&&&&&&&&&&&&&&@@        *@@############@
#                     *&/ @@ #&&&&&&&&&&&&&&&&&&&&@  ###################*
#                              @&&&&&&&&&&&&&&&&&&##################@
#                                 %@&&&&&&&&&&&&&&################@
#                                        @&&&&&&&&&&%#######&@%
#  nanaimo                                   (@&&&&####@@*
#
import argparse
import asyncio
import logging
import sys
import typing

import argcomplete

import nanaimo
from nanaimo.config import ArgumentDefaults


class CreateAndGatherFunctor:
    """
    Stores the type, manager, and loop then uses these to instantiate
    and invoke a Fixture if the given default is selected.
    Returns the result-code of the artifacts.
    """

    def __init__(self,
                 fixture_type: typing.Type['nanaimo.Fixture'],
                 manager: nanaimo.FixtureManager,
                 loop: asyncio.AbstractEventLoop):
        self._fixture_type = fixture_type
        self._manager = manager
        self._loop = loop
        self._logger = logging.getLogger(fixture_type.get_canonical_name())

    async def __call__(self, args: nanaimo.Namespace) -> int:
        fixture = self._fixture_type(self._manager, args, self._loop)
        artifacts = await fixture.gather()
        artifacts.dump(self._logger)
        return int(artifacts)


def _auto_brief(documented: typing.Any, default_brief: str = '') -> str:
    if documented is None or documented.__doc__ is None:
        return default_brief
    lines = documented.__doc__.strip().split('\n')  # type: typing.List[str]
    if len(lines) > 1:
        return '{}…'.format(lines[0])
    else:
        return lines[0]


def _visit_argparse(manager: nanaimo.FixtureManager,
                    subparsers: argparse._SubParsersAction,
                    loop: asyncio.AbstractEventLoop,
                    defaults: typing.Optional[ArgumentDefaults]) -> None:
    for fixture_type in manager.fixture_types():
        subparser = subparsers.add_parser(fixture_type.get_canonical_name(),
                                          help=_auto_brief(fixture_type))  # type: 'argparse.ArgumentParser'
        fixture_type.on_visit_test_arguments(nanaimo.Arguments(subparser, defaults))
        subparser.set_defaults(func=CreateAndGatherFunctor(fixture_type, manager, loop))


def _make_parser(loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                 defaults: typing.Optional[ArgumentDefaults] = None) -> argparse.ArgumentParser:
    """
    Defines the command-line interface. Provided as a separate factory method to
    support sphinx-argparse documentation.
    """

    epilog = '''**Example Usage**::

    python -m nanaimo -vv nanaimo_bar

----
'''

    if defaults is None:
        defaults = ArgumentDefaults()

    parser = argparse.ArgumentParser(
        description='Run tests against hardware.',
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter)

    from nanaimo.version import __version__

    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('--rcfile', help='Path to a default values configuration file.'
                                         'See nanaimo.Namespace for details.')
    parser.add_argument('--verbose', '-v', action='count',
                        help='verbosity level (-v, -vv)')

    subparsers = parser.add_subparsers(dest='fixture', help='Available fixtures.')

    pm = nanaimo.PluggyFixtureManager()

    _visit_argparse(pm, subparsers, loop, defaults)  # type: ignore

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
    defaults = ArgumentDefaults()

    parser = _make_parser(loop, defaults)
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    defaults.set_args(args)

    _setup_logging(args)

    if hasattr(args, 'func'):
        args_ns = nanaimo.Namespace(args, defaults)
        result = loop.run_until_complete(args.func(args_ns))
        try:
            return int(result)
        except ValueError:
            print('Nanaimo tests must return an int result!')
            raise
    else:
        parser.print_usage()
        return -1
