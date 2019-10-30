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

import logging


class ArgumentDefaults:
    """
    Manages default values for Nanaimo arguments. Use in conjunction with :class:`nanaimo.Arguments` and
    :class:`nanaimo.Namespace` to populate default argument values when adding arguments to pytest or argparse
    and to replace missing attributes with values from configuration.

    When using the Nanaimo CLI or pytest plugin you don't need to worry about this object as these modules
    wire up the defaults, arguments, and namespaces for you.
    """

    _default_read_locations = ['~/nanaimo.cfg', '/etc/nanaimo.cfg', 'setup.cfg']
    """
    These are all the locations that Nanaimo configuration files will be searched for.
    Configuration merge rules are as defined by :meth:`configparser.ConfigParser.read`.
    """

    @classmethod
    def createDefaultsWithEarlyRcConfig(cls) -> 'ArgumentDefaults':
        '''
        A special factory method that creates a :class:`ArgumentDefaults` instance pulling
        the value of ``--rcfile`` directly from :data:`sys.argv`. This allows defaults to
        be pulled from a config file before argument parsing is performed.
        '''
        import sys

        def args() -> None:
            pass

        for x in range(0, len(sys.argv) - 1):
            if sys.argv[x] == '--rcfile':
                setattr(args, 'rcfile', sys.argv[x+1])
                break

        return ArgumentDefaults(args)

    def __init__(self, args: typing.Optional[typing.Any] = None) -> None:
        self._env_variable_index = weakref.WeakKeyDictionary()  # type: weakref.WeakKeyDictionary
        self._configparser = configparser.ConfigParser()
        self._logger = logging.getLogger(__name__)
        if args is not None:
            self.set_args(args)
        else:
            self.set_args(dict())

    def set_args(self, args: typing.Any) -> None:
        if hasattr(args, 'rcfile') and args.rcfile is not None:
            read_locations = [str(args.rcfile)] + self._default_read_locations
        else:
            read_locations = self._default_read_locations
        read_from = self._configparser.read(read_locations)
        self._logger.debug('Configuration read from {}'.format(str(read_from)))

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

        # First replace any default with one from configuration.
        try:
            derived_key = self._derive_key_from_args(inout_args)
            from_config = self[derived_key]
            if from_config is not None:
                if 'type' in inout_kwargs:
                    inout_kwargs['default'] = inout_kwargs['type'](from_config)
                else:
                    inout_kwargs['default'] = from_config
                self._logger.debug('Setting the default for %s to %s (type %s) from a config file.',
                                   derived_key,
                                   inout_kwargs['default'],
                                   type(inout_kwargs['default']))
        except (KeyError, ValueError):
            pass

        # If we do have an environment variable and we allow this to be used
        # as a default it should become the default.
        if 'enable_default_from_environ' in inout_kwargs:
            if inout_kwargs['enable_default_from_environ']:
                self._handle_enable_default_from_environ(parser, inout_args, inout_kwargs)
            del inout_kwargs['enable_default_from_environ']

        # Finally, delete required if we managed to find a default.
        if 'required' in inout_kwargs and 'default' in inout_kwargs:
            # Since we have a default from configuration we can remove the required flag.
            del inout_kwargs['required']

    @classmethod
    def _derive_key_from_args(cls, inout_args: typing.Tuple) -> str:
        if len(inout_args) == 0:
            raise ValueError('No positional arguments')

        if len(inout_args) > 1:
            longform = str(inout_args[0]) if str(inout_args[0]).startswith('--') else str(inout_args[1])
        else:
            longform = str(inout_args[0])

        if not longform.startswith('--'):
            raise ValueError('No long-form argument to derive.')
        return longform[2:].replace('-', '_')

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
        if env_variable in os.environ:
            inout_kwargs['default'] = os.environ[env_variable]
            try:
                inout_kwargs['default'] = inout_kwargs['type'](inout_kwargs['default'])
            except KeyError:
                pass
            additional_help = 'Default value {} obtained from environment variable {}.'\
                .format(os.environ[env_variable], env_variable)
        else:
            additional_help = 'Set {} in the environment to override default.'.format(env_variable)
        try:
            inout_kwargs['help'] = inout_kwargs['help'] + '\n' + additional_help
        except KeyError:
            inout_kwargs['help'] = additional_help
