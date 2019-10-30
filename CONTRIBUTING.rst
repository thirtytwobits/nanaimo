#####################
Contributor Notes
#####################

Hi! Thanks for contributing. This page contains all the details about getting
your dev environment setup.

.. note::

    This is documentation for contributors developing nanaimo. If you are
    a user of this software you can ignore everything here.

************************************************
Tools
************************************************

virtualenv
================================================

I highly recommend using a virtual environment when doing python development. It'll save you
hours of lost productivity the first time it keeps you from pulling in an unexpected dependency
from your global python environment. You can install virtualenv from brew on osx or apt-get on
linux. I'd recommend the following environment for vscode::

    virtualenv -p python3.7 .pyenv
    source .pyenv/bin/activate
    pip install -r requirements.txt
    pip -e install .


Visual Studio Code
================================================

Provided is a .vscode folder with recommended extensions and settings to get you started. Cd into the
Nanaimo repository, source your virtualenv (see virtualenv_) and then launch vscode using `code .`.


************************************************
Running The Tests
************************************************

To run the full suite of `tox`_ tests locally you'll need docker. Once you have docker installed
and running do::

    docker pull uavcan/toxic:py35-py38-sq
    docker run --rm -it -v $PWD:/repo uavcan/toxic:py35-py38-sq
    tox

To run tests for a single version of python specify the environment as such ::

    tox -e py36-test

And to run a single test for a single version of python do::

    tox -e py36-test -- -k test_program_uploader_failure


Sybil Doctest
================================================

This project makes extensive use of `Sybil <https://sybil.readthedocs.io/en/latest/>`_ doctests.
These take the form of docstrings with a structure like thus::

    .. invisible-code-block: python

        from foo import bar

    .. code-block:: python

        # Use bar method to transform baz

    >>> bar('baz')  # noqa : F821
    'braz'

The invisible code block is executed but not displayed in the generated documentation and,
conversely, ``code-block`` is both rendered using proper syntax formatting in the documentation
and executed. REPL works the same as it does for :mod:`doctest` but ``assert`` is also a valid
way to ensure the example is correct especially if used in a trailing ``invisible-code-block``.

These tests are run as part of the regular pytest build. You can see the Sybil setup in the
``conftest.py`` found under the root directory but otherwise shouldn't need to worry about
it. The simple rule is; if the docstring ends up in the rendered documentation then your
``code-block`` tests will be executed as unit tests.


************************************************
Running Reports and Generating Docs
************************************************

Documentation
================================================

We rely on `read the docs`_ to build our documentation from github but we also verify this build
as part of our tox build. This means you can view a local copy after completing a full, successful
test run (See `Running The Tests`_) or do
:code:`docker run --rm -t -v $PWD:/repo uavcan/toxic:py35-py38-sq /bin/sh -c "tox -e docs"` to build
the docs target. You can open the index.html under .tox/docs/tmp/index.html or run a local
web-server::

    python -m http.server --directory .tox/docs/tmp &
    open http://localhost:8000/index.html


Coverage
================================================

We generate a local html coverage report. You can open the index.html under .tox/report/tmp
or run a local web-server::

    python -m http.server --directory .tox/report/tmp &
    open http://localhost:8000/index.html

Mypy
================================================

At the end of the mypy run we generate the following summaries:

- .tox/mypy/tmp/mypy-report-lib/index.txt
- .tox/mypy/tmp/mypy-report-script/index.txt


.. _`read the docs`: https://readthedocs.org/
.. _`tox`: https://tox.readthedocs.io/en/latest/
