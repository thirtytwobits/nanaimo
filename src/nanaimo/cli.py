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
import textwrap
import typing

import argcomplete

import nanaimo
import nanaimo.fixtures
import nanaimo.config


class CreateAndGatherFunctor:
    """
    Stores the type, manager, and loop then uses these to instantiate
    and invoke a Fixture if the given default is selected.
    Returns the result-code of the artifacts.
    """

    def __init__(self,
                 fixture_type: typing.Type[nanaimo.fixtures.Fixture],
                 manager: nanaimo.fixtures.FixtureManager,
                 loop: asyncio.AbstractEventLoop):
        self._fixture_type = fixture_type
        self._manager = manager
        self._loop = loop
        self._logger = logging.getLogger(fixture_type.get_canonical_name())

    async def __call__(self, args: nanaimo.Namespace, gather_timeout_seconds: typing.Optional[float] = None) -> int:
        fixture = self._fixture_type(self._manager,
                                     args,
                                     loop=self._loop,
                                     gather_timeout_seconds=gather_timeout_seconds)
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


def _visit_argparse(manager: nanaimo.fixtures.FixtureManager,
                    subparsers: argparse._SubParsersAction,
                    loop: asyncio.AbstractEventLoop,
                    defaults: typing.Optional[nanaimo.config.ArgumentDefaults]) -> None:
    for fixture_type in manager.fixture_types():
        subparser = subparsers.add_parser(fixture_type.get_canonical_name(),
                                          help=_auto_brief(fixture_type))  # type: 'argparse.ArgumentParser'
        fixture_type.on_visit_test_arguments(nanaimo.Arguments(subparser, defaults, fixture_type.get_argument_prefix()))
        subparser.set_defaults(func=CreateAndGatherFunctor(fixture_type, manager, loop))


def _make_parser(loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                 defaults: typing.Optional[nanaimo.config.ArgumentDefaults] = None) -> argparse.ArgumentParser:
    """
    Defines the command-line interface. Provided as a separate factory method to
    support sphinx-argparse documentation.
    """

    epilog = '''**Example Usage**::

    python -m nanaimo -vv nanaimo_bar

----
'''

    if defaults is None:
        defaults = nanaimo.config.ArgumentDefaults()

    parser = argparse.ArgumentParser(
        description='Run tests against hardware.',
        epilog=epilog,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    from nanaimo.version import __version__

    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('--rcfile', help='Path to a default values configuration file.'
                                         'See nanaimo.Namespace for details.')
    parser.add_argument('--log-level', choices=['WARNING', 'INFO', 'DEBUG', 'VERBOSE_DEBUG'],
                        help='python logging level.')

    parser.add_argument('--gather-timeout-seconds',
                        type=float,
                        help=textwrap.dedent('''
                            A gather timeout in fractional seconds to use for all fixtures.
                            If not provided then Fixture.gather will not timeout.''').lstrip())

    subparsers = parser.add_subparsers(dest='fixture', help='Available fixtures.')

    pm = nanaimo.fixtures.PluggyFixtureManager()

    _visit_argparse(pm, subparsers, loop, defaults)  # type: ignore

    return parser


def _setup_logging(args: nanaimo.Namespace) -> None:
    fmt = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    if args.log_level == 'WARNING':
        level = logging.WARNING
    elif args.log_level == 'DEBUG':
        level = logging.DEBUG
    elif args.log_level == 'VERBOSE_DEBUG':
        level = logging.DEBUG
        logging.getLogger('asyncio').setLevel(logging.DEBUG)
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format=fmt, datefmt='%Y-%m-%d %H:%M:%S')
    if level <= logging.INFO:
        logging.getLogger(__name__).info('Nanaimo logging is configured.')


def main() -> int:
    """
    CLI entrypoint for running Nanaimo tests.
    """

    loop = asyncio.get_event_loop()
    defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()

    parser = _make_parser(loop, defaults)
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    defaults.set_args(args)

    args_ns = nanaimo.Namespace(args, defaults, allow_none_values=False)

    _setup_logging(args_ns)

    if hasattr(args, 'func'):
        result = loop.run_until_complete(args.func(args_ns, args_ns.gather_timeout_seconds))
        try:
            return int(result)
        except ValueError:
            logging.getLogger(__name__).error('Nanaimo tests must return an int result!')
            raise
    else:
        parser.print_usage()
        return -1
