#!/usr/bin/env python
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
import sys


def main() -> int:
    """
    Entrypoint for ``nait`` which synthesizes a pytest for each fixture name as an function
    asserting success on the fixture's gather method. For example, given ::

        nait nanaimo_bar

    ... the following, equivalent test function would be synthesized ::

        test_nanaimo_bar(pytest_args, nanaimo_bar):
            assert_success(nanaimo_bar.gather(**pytest_args))

    """
    if '--environ-shell' in sys.argv or '-S' in sys.argv:
        import nanaimo
        defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()
        args_ns = nanaimo.Namespace(defaults=defaults, allow_none_values=False)
        for key, value in args_ns.get_as_merged_dict('environ').items():
            print('export {}="{}";'.format(key, value), end='')
        argv_len = len(sys.argv)
        for x in range(0, argv_len):
            if sys.argv[x] == '--environ' and x < argv_len - 1:
                environ_pair = sys.argv[x+1].split('=')
                if len(environ_pair) == 2:
                    print('export {}="{}";'.format(environ_pair[0].strip(), environ_pair[1].strip()))
        return 0
    if '--version' in sys.argv:
        from nanaimo.version import __version__
        print(__version__)
        return 0
    import nanaimo.pytest.plugin
    import pytest
    nanaimo.pytest.plugin._nait_mode = True
    return pytest.main()
