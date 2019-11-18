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
This module contains the common types used by Nanaimo.

"""
import argparse
import logging
import os
import typing

from .config import ArgumentDefaults


class AssertionError(RuntimeError):
    """
    Thrown by Nanaimo tests when an assertion has failed.

    .. Note::
        This exception should be used only when the state of a :class:`nanaimo.fixtures.Fixture`
        was invalid. You should use pytest tests and assertions when writing validation
        cases for fixture output like log files or sensor data.
    """
    pass


class Arguments:
    """
    Adapter for pytest and argparse parser arguments.

    :param inner_arguments: Either a pytest group (unpublished type returned from :meth:`pytest.Parser.getgroup`)
        or a :class:`argparse.ArgumentParser`
    :param typing.Any defaults: Optional provider of default values for arguments.
    :type defaults: typing.Optional[ArgumentDefaults]
    :param str required_prefix: If provided :meth:`add_argument` will rewrite arguments to enure they have the required
        prefix.
    :param bool filter_duplicates: If true then this class will track keys provided to the :meth:`add_argument` method
        and will not call the inner object if duplicates are detected. If false then all calls to :meth:`add_argument`
        are always forwarded to the inner object. This filter is tracked per instance so duplicates provided to
        different instances are not filtered.
    """

    def __init__(self,
                 inner_arguments: typing.Any,
                 defaults: typing.Optional[ArgumentDefaults] = None,
                 required_prefix: typing.Optional[str] = None,
                 filter_duplicates: bool = False):
        self._inner = inner_arguments
        self._defaults = defaults
        self._required_prefix = (required_prefix.replace('_', '-') if required_prefix is not None else None)
        self._logger = logging.getLogger(__name__)
        self._key_set = (set() if filter_duplicates else None)  # type: typing.Optional[typing.Set[str]]

    @property
    def required_prefix(self) -> typing.Optional[str]:
        return self._required_prefix

    @required_prefix.setter
    def required_prefix(self, value: typing.Optional[str]) -> None:
        self._required_prefix = value

    def set_inner_arguments(self, inner_arguments: typing.Any) -> None:
        """
        Reset the inner argument object this object wraps. This method allows a single instance to filter
        all arguments preventing duplicates from reading the inner objects.

        .. invisible-code-block: python
            from nanaimo import Arguments
            from unittest.mock import MagicMock
            import argparse

            parser = MagicMock(spec=argparse.ArgumentParser)
            parser.add_argument = MagicMock()

            my_other_parser = MagicMock(spec=argparse.ArgumentParser)
            my_other_parser.add_argument = MagicMock()

        .. code-block:: python

            a = Arguments(parser, filter_duplicates=True)
            a.add_argument('--foo')

            # This second call will not make it to the parser
            # object we set above.
            a.add_argument('--foo')

            # If we set another parser on the same Arguments instance...
            a.inner_arguments = my_other_parser

            # then the same filter will continue to apply for this new
            # inner argument object.
            a.add_argument('--foo')

        .. invisible-code-block: python

            parser.add_argument.assert_called_once_with('--foo')
            my_other_parser.add_argument.assert_not_called()

        """
        self._inner = inner_arguments

    def add_argument(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """
        This method invokes :meth:`argparse.ArgumentParser.add_argument` but with one additional argument:
        ``enable_default_from_environ``. If this is provided as True then a default value will be taken from
        an environment variable derived from the long form of the argument:

        .. invisible-code-block: python
            from nanaimo import Arguments
            from unittest.mock import MagicMock, ANY
            from nanaimo.config import ArgumentDefaults
            import argparse
            import os

            parser = argparse.ArgumentParser()
            parser.add_argument = MagicMock()
            config = ArgumentDefaults()

        .. code-block:: python

            # Using...
            long_arg = '--baud-rate'

            # ...the environment variable looked for will be:
            environment_var_name = 'NANAIMO_BAUD_RATE'

            # If we set the environment variable...
            os.environ[environment_var_name] = '115200'

            a = Arguments(parser, config)

            # ...and provide a default...
            a.add_argument('--baud-rate',
                           default=9600,
                           type=int,
                           enable_default_from_environ=True,
                           help='Will be 9600 unless argument is provided.')

            # ...the actual default value will be 115200

        .. invisible-code-block: python

            parser.add_argument.assert_called_once_with('--baud-rate', default=115200, type=int, help=ANY)

            add_argument_call_args = parser.add_argument.call_args[1]

        .. code-block:: python

            assert add_argument_call_args['default'] == 115200

        .. invisible-code-block: python

            parser.add_argument = MagicMock()

        .. code-block:: python

            # Using a required prefix...
            a = Arguments(parser, config, required_prefix='ad')

            # ...and adding an argument...
            a.add_argument('--baud-rate')

            # ...the actual argument added will be
            actual_long_arg = '--ad-baud-rate'

        .. invisible-code-block: python

            parser.add_argument.assert_called_once_with(actual_long_arg)

        """
        if self._required_prefix is not None:
            args = self._rewrite_with_prefix(args)

        if self._key_set is not None:
            # Pytest has a bug where the ValueError thrown from
            # addoption leaves their parser in an inconsistent state.
            # The only way to handle duplicate resolution with pytest
            # is to intercept duplicates before they reach their
            # option parser.
            long_form_index, long_form = self._preparse_args(args)
            if long_form in self._key_set:
                self._logger.debug('Filtering duplicate key %s', long_form)
                return
            self._key_set.add(long_form)

        if self._defaults is not None:
            self._defaults.populate_default(self._inner, args, kwargs)

        if isinstance(self._inner, argparse.ArgumentParser):
            self._inner.add_argument(*args, **kwargs)
        else:
            self._inner.addoption(*args, **kwargs)

    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+
    @classmethod
    def _preparse_args(cls, args: typing.Tuple) -> typing.Tuple[int, str]:
        if len(args) == 0:
            raise AttributeError('No positional args provided?')

        long_form_index = -1
        for i in range(0, len(args)):
            if args[i].startswith('--'):
                long_form_index = i
                break

        return (long_form_index, args[long_form_index])

    def _rewrite_with_prefix(self, inout_args: typing.Tuple) -> typing.Tuple:

        long_form_index, long_form = self._preparse_args(inout_args)

        if long_form_index >= 0 and not inout_args[long_form_index].startswith('--{}'.format(self._required_prefix)):
            as_list = list(inout_args)
            rewritten = '--{}{}'.format(self._required_prefix, long_form[1:])
            self._logger.debug('Rewriting argument {} to {} because it was missing required prefix "{}".'
                               .format(long_form,
                                       rewritten,
                                       self._required_prefix))
            return tuple(as_list[:long_form_index] + [rewritten] + as_list[long_form_index + 1:])
        else:
            return inout_args


class Namespace:
    """
    Generic object that acts like :class:`argparse.Namespace` but can be created using pytest
    plugin arguments as well.

    If :class:`nanaimo.config.ArgumentDefaults` are used with the :class:`Arguments` and this class then a given
    argument's value will be resolved in the following order:

        1. provided value
        2. config file specified by --rcfile argument.
        3. nanaimo.cfg in user directory
        4. nanaimo.cfg in system directory
        5. default from environment (if ``enable_default_from_environ`` was set for the argument)
        6. default specified for the argument.

    This is accomplished by first rewriting the defaults when attributes are defined on the :class:`Arguments`
    class and then capturing missing attributes on this class and looking up default values from configuration
    files.

    For lookup steps involving configuration files (where :class:`configparser.ConfigParser` is used internally)
    the lookup will search the configuration space using underscores ``_`` as namespace separators. this search
    will proceed as follows:

    .. invisible-code-block: python

        from nanaimo.config import ArgumentDefaults
        from unittest.mock import MagicMock, ANY
        import nanaimo

        argument_defaults = ArgumentDefaults()
        argument_defaults._configparser = MagicMock()

        values = MagicMock()
        count = 0

        def seventh_times_a_charm(_):
            global count, values
            count += 1
            if count < 7:
                raise KeyError
            return values

        argument_defaults._configparser.__getitem__.side_effect = seventh_times_a_charm

    .. code-block:: python

        # given
        key = 'a_b_c_d'

        # the following lookups will occur
        config_lookups = {
            'nanaimo:a_b_c': 'd',
            'nanaimo:a_b': 'c_d',
            'nanaimo:a': 'b_c_d',
            'a_b_c': 'd',
            'a_b': 'c_d',
            'a': 'b_c_d',
            'nanaimo': 'a_b_c_d'
        }

        # when using an ArgumentDefaults instance
        _ = argument_defaults[key]

    .. invisible-code-block: python

        for item in config_lookups.items():
            argument_defaults._configparser.__getitem__.assert_any_call(item[0])
        values.__getitem__.assert_any_call('a_b_c_d')

    So for a given configuration file::

        [nanaimo]
        a_b_c_d = 1

        [a]
        b_c_d = 2

    the value ``2`` under the ``a`` group will override (i.e. mask) the value ``1`` under the ``nanaimo`` group.

    .. note ::

        A specific example:

        - ``--bk-port <value>`` – if provided on the commandline will always override everything.
        - ``[bk] port = <value>`` – in a config file will be found next if no argument was given on the commandline.
        - ``NANAIMO_BK_PORT`` - set in the environment will be used if no configuration was provided because
          the :mod:`nanaimo.instruments.bkprecision` module defines the ``bk-port`` argument with
          ``enable_default_from_environ`` set.

    This object has a somewhat peculiar behavior for Python. All attributes will be reported either as a found value or
    as ``None``. That is, any arbitrary attribute requested from this object will be ``None``. To differentiate between
    ``None`` and "not set" you must using ``in``:

    .. code-block:: python

        ns = nanaimo.Namespace()
        assert ns.foo is None
        assert 'foo' not in ns

    The behavior was designed to simplify argument handling code since argparse Namespaces will have ``None`` values for
    all arguments even if the were not provided and had no default value.

    :param parent: A namespace-like object to inherit attributes from.
    :type parent: typing.Optional[typing.Any]
    :param defaults: Defaults to use if a requested attribute is not available on this object.
    :type defaults: typing.Optional[ArgumentDefaults]
    :param allow_none_values: If True then an attribute with a None value is considered valid otherwise
        any attribute that is None will cause the Namespace to search for a non-None value in the defaults.
    :type allow_none_values: bool
    """

    def __init__(self,
                 parent: typing.Optional[typing.Any] = None,
                 defaults: typing.Optional[ArgumentDefaults] = None,
                 allow_none_values: bool = True):
        self._defaults = defaults
        if parent is not None:
            for key in vars(parent):
                parent_value = getattr(parent, key)
                if allow_none_values or parent_value is not None:
                    setattr(self, key, parent_value)

    def __getattr__(self, key: str) -> typing.Any:
        try:
            return self.__dict__[key]
        except KeyError:
            if self._defaults is None:
                return None
        try:
            return self._defaults[key]
        except KeyError:
            return None

    def __contains__(self, key: str) -> typing.Any:
        if key in self.__dict__:
            return True
        elif self._defaults is None:
            return False
        else:
            return key in self._defaults

    def get_as_merged_dict(self, key: str) -> typing.Mapping[str, typing.Any]:
        """
        Expect the value to be a dictionary. In this case also load the defaults into
        the dictionary.

        :param key: The key to load the dictionary from.
        """
        result = dict()  # type: typing.Dict[str, typing.Any]
        if self._defaults is not None:
            try:
                result.update(ArgumentDefaults.as_dict(self._defaults[key]))
            except KeyError:
                pass
        try:
            result.update(ArgumentDefaults.as_dict(self.__dict__[key]))
        except KeyError:
            pass
        return result

    T = typing.TypeVar('T')

    def merge(self, **kwargs: typing.Any) -> 'Namespace.T':
        """
        Merges a list of keyword arguments with this namespace and returns a new, merged
        Namespace. This does not modify the instance that merge is called on.

        Example:

        .. invisible-code-block: python
            from nanaimo import Namespace

        .. code-block:: python

            original = Namespace()
            setattr(original, 'foo', 1)

            assert 1 == original.foo

            merged = original.merge(foo=2, bar='hello')

            assert 1 == original.foo
            assert 2 == merged.foo
            assert 'hello' == merged.bar

        :return: A new namespace with the contents of this object and any values provided as
            kwargs overwriting the values in this instance where the keys are the same.
        """
        merged = self.__class__(parent=self, defaults=self._defaults)
        for key in kwargs:
            setattr(merged, key, kwargs[key])
        return typing.cast('Namespace.T', merged)


class Artifacts(Namespace):
    """
    Namespace returned by :class:`nanaimo.fixtures.Fixture` objects when invoked that contains the artifacts collected
    from the fixture's activities.

    :param result_code: The value to report as the status of the activity that gathered the artifacts.
    :param parent: A namespace-like object to inherit attributes from.
    :type parent: typing.Optional[typing.Any]
    :param defaults: Defaults to use if a requested attribute is not available on this object.
    :type defaults: typing.Optional[ArgumentDefaults]
    :param allow_none_values: If True then an attribute with a None value is considered valid otherwise
        any attribute that is None will cause the Artifacts to search for a non-None value in the defaults.
    :type allow_none_values: bool
    """

    @classmethod
    def combine(cls, *artifacts: 'Artifacts') -> 'Artifacts':
        '''
        Combine a series of artifacts into a single instance.
        This method uses :meth:`Namespace.merge` but adds additional semantics including:

        .. note ::

            While this method does not modify the original objects it also does not do a deep
            copy of artifact values.

        .. invisible-code-block: python
            from nanaimo import Artifacts

            first = Artifacts()
            setattr(first, 'foo', 1)
            second = Artifacts()
            setattr(second, 'bar', 2)

            combined = Artifacts.combine(first, second)
            assert 1 == combined.foo
            assert 2 == combined.bar

        Given two :class:`Artifacts` objects with the same attribute the right-most item in the
        combine list will overwrite the previous values and become the only value:

        .. code-block:: python

            setattr(first, 'foo', 1)
            setattr(second, 'foo', 2)

            assert Artifacts.combine(first, second).foo == 2
            assert Artifacts.combine(second, first).foo == 1

        The :data:`result_code` of the combined value will be either 0 iff all combined
        Artifact objects have a result_code of 0:

        .. code-block:: python

            first.result_code = 0
            second.result_code = 0

            assert Artifacts.combine(first, second).result_code == 0

        or will be non-zero if any instance had a non-zero result code:

        .. code-block:: python

            first.result_code = 0
            second.result_code = 1

            assert Artifacts.combine(first, second).result_code != 0

        :param artifacts: A list of artifacts to combine into a single :class:`Artifacts` instance.
        :raises ValueError: if no artifact objects were provided or if the method was otherwise unable to
            create a new object from the provided ones.
        '''
        combined = None
        result_codes_were_all_zeros = True
        for a in artifacts:
            if combined is not None:
                combined = combined.merge(**a.__dict__)
            else:
                combined = a
            if a.result_code != 0:
                result_codes_were_all_zeros = False
        if combined is None:
            raise ValueError('Nothing to combine.')
        combined.result_code = (0 if result_codes_were_all_zeros else -1)
        return combined

    def __init__(self,
                 result_code: int = 0,
                 parent: typing.Optional[typing.Any] = None,
                 defaults: typing.Optional[ArgumentDefaults] = None,
                 allow_none_values: bool = True):
        super().__init__(parent=parent, defaults=defaults, allow_none_values=allow_none_values)
        self._result_code = result_code

    @property
    def result_code(self) -> int:
        """
        0 if the artifacts were retrieved without error. Non-zero if some error
        occurred. The contents of this :class:`Namespace` is undefined for non-zero
        result codes.
        """
        return self._result_code

    @result_code.setter
    def result_code(self, new_result: int) -> None:
        self._result_code = new_result

    def dump(self, logger: logging.Logger, log_level: int = logging.DEBUG) -> None:
        """
        Dump a human readable representation of this object to the given logger.
        :param logger:  The logger to use.
        :param log_level: The log level to dump the object as.
        """
        try:
            import yaml
            try:
                logger.log(log_level, yaml.dump(vars(self)))
            except TypeError:
                logger.log(log_level, '(failed to serialize Artifacts)')
        except ImportError:
            logger.log(log_level, str(vars(self)))

    def __int__(self) -> int:
        """
        Converts a reference to this object into its `result_code`.
        """
        return self._result_code


def assert_success(artifacts: Artifacts) -> Artifacts:
    """
    Syntactic sugar to allow more fluent handling of :meth:`fixtures.Fixture.gather`
    artifacts. For example:

    .. invisible-code-block: python

        import asyncio
        from nanaimo import Artifacts, assert_success
        from nanaimo.fixtures import Fixture, FixtureManager

        _doc_loop = asyncio.new_event_loop()

        class DummyFixture(Fixture):
            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                pass

            async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                return nanaimo.Artifacts()

        fixture = DummyFixture(FixtureManager(loop=_doc_loop))

    .. code-block:: python

        async def test_my_fixture():

            artifacts = assert_success(await fixture.gather())

            # Now we can use the artifacts. If the gather had returned
            # non-zero for the result_code an assertion error would have
            # been raised.

    .. invisible-code-block: python

        _doc_loop.run_until_complete(test_my_fixture())

    :param artifacts: The artifacts to assert on.
    :type artifacts: nanaimo.Artifacts
    :returns: artifacts (for convenience).
    :rtype: nanaimo.Artifacts()
    """
    assert artifacts.result_code == 0
    return artifacts


def assert_success_if(artifacts: Artifacts, conditional: typing.Callable[[Artifacts], bool]) -> Artifacts:
    """
    Syntactic sugar to allow more fluent handling of :meth:`fixtures.Fixture.gather`
    artifacts but with a user-supplied conditional.

    .. invisible-code-block: python

        import asyncio
        import pytest
        from nanaimo import Artifacts, assert_success_if
        from nanaimo.fixtures import Fixture, FixtureManager

        _doc_loop = asyncio.new_event_loop()

        class DummyFixture(Fixture):
            @classmethod
            def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
                pass

            async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
                a = nanaimo.Artifacts()
                setattr(a, 'foo', 'bar')
                return a

        fixture = DummyFixture(FixtureManager(loop=_doc_loop))

    .. code-block:: python

        async def test_my_fixture():

            def fail_if_no_foo(artifacts: Artifacts) -> bool:
                return 'foo' in artifacts

            artifacts = assert_success_if(await fixture.gather(), fail_if_no_foo)

            print('artifacts have foo. It\'s value is {}'.format(artifacts.foo))

    .. invisible-code-block: python

        _doc_loop.run_until_complete(test_my_fixture())

        async def test_failure():

            assert_success_if(await fixture.gather(), lambda _: False)

        with pytest.raises(nanaimo.AssertionError):
            _doc_loop.run_until_complete(test_failure())

    :param artifacts: The artifacts to assert on.
    :type artifacts: nanaimo.Artifacts
    :param conditiona: A method called to evaluate gathered artifacts iff :data:`Artifacts.result_code` is 0.
        Return False to trigger an assertion, True to pass.
    :returns: artifacts (for convenience).
    :rtype: nanaimo.Artifacts()
    """
    assert artifacts.result_code == 0
    assert conditional(artifacts)
    return artifacts


def set_subprocess_environment(args: Namespace) -> None:
    """
    Updates :data:`os.environ` from values set as ``environ`` in the provided arguments.

    :param args: A namespace to load the environment from. The map of values in this key are
        added to any subsequent subprocess started but can be overridden by ``env`` arguments to
        subprocess constructors like :class:`subprocess.Popen`
    :type defaults: Namespace
    """
    os.environ.update(args.get_as_merged_dict('environ'))
