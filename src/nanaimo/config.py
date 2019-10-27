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
"""
Much of what Nanaimo does is to allow for intuitive, intelligent, and adaptable configuration of fixtures. This module
contains internal implementations used by public types to facilitate this functionality.
"""
import argparse
import configparser
import os
import typing
import weakref


class ArgumentDefaults:
    """
    Manages default values for Nanaimo arguments. Use in conjunction with :class:`nanaimo.Arguments` and
    :class:`nanaimo.Namespace` to populate default argument values when adding arguments to pytest or argparse
    and to replace missing attributes with values from configuration.

    When using the Nanaimo CLI or pytest plugin you don't need to worry about this object as these modules
    wire up the defaults, arguments, and namespaces for you.
    """

    _default_read_locations = ['~/nanaimo.cfg', '/etc/nanaimo.cfg']
    """
    These are all the locations that Nanaimo configuration files will be searched for.
    Configuration merge rules are as defined by :meth:`configparser.ConfigParser.read`.
    """

    def __init__(self, args: typing.Optional[typing.Any] = None) -> None:
        self._env_variable_index = weakref.WeakKeyDictionary()  # type: weakref.WeakKeyDictionary
        self._configparser = configparser.ConfigParser()
        if args is not None:
            self.set_args(args)
        else:
            self._configparser.read(self._default_read_locations)

    def set_args(self, args: typing.Any) -> None:
        if hasattr(args, 'rcfile') and args.rcfile is not None:
            read_locations = [str(args.rcfile)] + self._default_read_locations
        else:
            read_locations = self._default_read_locations
        self._configparser.read(read_locations)

    def __getitem__(self, key: str) -> typing.Any:
        namespaced_key = key.split('_')
        # Try once with nanaimo prefix (more specific)
        for x in range(len(namespaced_key)-1, 0, -1):
            try:
                group = '_'.join(namespaced_key[:x])
                value_key = '_'.join(namespaced_key[x:])
                return self._configparser['nanaimo:' + group][value_key]
            except KeyError:
                pass

        # Try again without the prefix
        for x in range(len(namespaced_key)-1, 0, -1):
            try:
                group = '_'.join(namespaced_key[:x])
                value_key = '_'.join(namespaced_key[x:])
                return self._configparser[group][value_key]
            except KeyError:
                pass

        return self._configparser['nanaimo'][key]

    def __contains__(self, key: str) -> bool:
        try:
            _ = self[key]
            return True
        except KeyError:
            return False

    def populate_default(self,
                         parser: argparse.ArgumentParser,
                         inout_args: typing.Tuple,
                         inout_kwargs: typing.Dict) -> None:

        if 'enable_default_from_environ' in inout_kwargs:
            if inout_kwargs['enable_default_from_environ']:
                self._handle_enable_default_from_environ(parser, inout_args, inout_kwargs)
            del inout_kwargs['enable_default_from_environ']
        if 'required' in inout_kwargs and 'default' not in inout_kwargs:
            inout_kwargs['default'] = self[self._derive_key_from_args(inout_args)]

    @classmethod
    def _derive_key_from_args(cls, inout_args: typing.Tuple) -> str:
        if len(inout_args) == 0:
            raise ValueError('No positional arguments')

        if len(inout_args) > 1:
            longform = str(inout_args[0]) if str(inout_args[0]).startswith('--') else str(inout_args[1])
        else:
            longform = str(inout_args[0])

        if not longform.startswith('--'):
            raise ValueError('Cannot synthesize environment variable without a long-form argument.')
        return longform[2:]

    def _handle_enable_default_from_environ(self,
                                            parser: argparse.ArgumentParser,
                                            inout_args: typing.Tuple,
                                            inout_kwargs: typing.Dict) -> None:
        name = self._derive_key_from_args(inout_args)

        env_variable = 'NANAIMO_{}'.format(name.upper().replace('-', '_'))
        try:
            parser_map = self._env_variable_index[parser]
            if env_variable in parser_map:
                raise RuntimeError('{} (derived from {}) was already derived from {}!'
                                   .format(env_variable, name,
                                           parser_map[env_variable]))
            parser_map[parser][env_variable] = name
        except KeyError:
            self._env_variable_index[parser] = {env_variable: name}
        self._set_default_from_environment(env_variable, inout_args, inout_kwargs)

    @classmethod
    def _set_default_from_environment(cls, env_variable: str, args: typing.Tuple, inout_kwargs: typing.Dict) -> None:
        try:
            inout_kwargs['default'] = os.environ.get(env_variable, inout_kwargs['default'])
        except KeyError:
            inout_kwargs['default'] = os.environ.get(env_variable, None)

        if inout_kwargs['default'] is not None:
            try:
                inout_kwargs['default'] = inout_kwargs['type'](inout_kwargs['default'])
            except KeyError:
                pass

        if env_variable in os.environ:
            additional_help = 'Default value {} obtained from environment variable {}.'\
                .format(os.environ[env_variable], env_variable)
        else:
            additional_help = 'Set {} in the environment to override default.'.format(env_variable)
        try:
            inout_kwargs['help'] = inout_kwargs['help'] + '\n' + additional_help
        except KeyError:
            inout_kwargs['help'] = additional_help
