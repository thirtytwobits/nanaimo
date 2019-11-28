.. _nait:

*************************************
nait (NanAimo Interactive Terminal)
*************************************

Usage::

    nait --help
    nait --fixtures

The commandline ``nait`` is installed with the nanaimo package and provides direct access to
nanaimo fixtures without having to write pytests. The CLI still uses pytest but synthesizes
tests based on the fixtures provided. See :ref:`fixtures_reference` for fixture names and arguments.

Example::

    > nait nanaimo_bar

    ------------------------------------ live log call -------------------------------------
    2019-12-18 16:49:34 DEBUG nanaimo.config: Configuration read from ['/etc/nanaimo.cfg', 'setup.cfg', 'tox.ini']
    2019-12-18 16:49:34 INFO nanaimo_bar: don't forget to eat your dessert.
    PASSED                                                                           [100%]

    --------------------------------------- nanaimo ----------------------------------------
    Fixture(s) "nanaimo_bar" result = 0
    .............................. Artifacts for nanaimo_bar ...............................
    eat=functools.partial(<bound method Logger.info of <Logger nanaimo_bar (DEBUG)>>, 'Nanaimo bars are yummy.')
    bar_None=0.42314194
    ================================== 1 passed in 0.02s ===================================

    > nait nanaimo_cmd -C 'nait --help'

    ------------------------------------ live log call -------------------------------------
    2019-12-18 16:51:35 DEBUG nanaimo.config: Configuration read from ['/etc/nanaimo.cfg', 'setup.cfg', 'tox.ini']
    2019-12-18 16:51:35 DEBUG nanaimo_cmd: About to execute command "nait --help" in a subprocess shell
    2019-12-18 16:51:36 INFO nanaimo_cmd: usage: nait [options] [nanaimo_fixture] [nanaimo_fixture] [...]
    2019-12-18 16:51:36 DEBUG nanaimo_cmd: command "nait --help" exited with 0
    PASSED                                                                           [100%]

    --------------------------------------- nanaimo ----------------------------------------
    Fixture(s) "nanaimo_cmd" result = 0
    .............................. Artifacts for nanaimo_cmd ...............................
    ================================== 1 passed in 0.47s ===================================

You are also invoking pytest so all pytest arguments apply. Use ``nait --help`` to see a listing of arguments
and ``nait --fixtures`` to see all available fixtures.

Special Arguments
===================================================================================================

The following arguments are specific to nait and are not the same as when invoking ``pytest`` directly:

- ``--version`` – List the version of Nanaimo (`not` pytest).
- ``-S`` or ``--environ-shell`` – List all environment variables provided to subprocess shells in shell syntax.
  This allows applying the subprocess environment to your current session by doing (in bash) ``eval $(nait -S)``
- ``--environ`` – A key=value argument to define environment variables in a subprocess shell. You can provide
  multiple arguments for example ::

    nait --environ foo=bar --environ baz=biz -S
- ``--concurrent`` – Runs multiple fixtures concurrently ::

    # Runs two nanaimo_bar fixtures one after the other
    nait nanaimo_bar nanaimo_bar

    # Runs two nanaimo_bar fixtures concurrently
    nait --concurrent nanaimo_bar nanaimo_bar
