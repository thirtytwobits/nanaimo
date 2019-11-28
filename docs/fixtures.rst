.. _fixtures_reference:

############################################
Fixtures Reference
############################################

This page provides a reference for the available fixtures in Nanaimo. While the
:ref:`nanaimo` guide is comprehensive it is useful only if you are writing your
own fixtures. This page provides a more concise reference when writing tests using
only Nanaimo's built-in fixtures and pytest plugins.


Builtin Pytest Fixtures
-------------------------------------------------

A set of pytest fixtures that come with nanaimo.

|pytest logo| nanaimo_arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: nanaimo.pytest.plugin.nanaimo_arguments
    :noindex:

|pytest logo| nanaimo_log
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: nanaimo.pytest.plugin.nanaimo_log
    :noindex:

|pytest logo| nanaimo_fixture_manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: nanaimo.pytest.plugin.nanaimo_fixture_manager
    :noindex:

Builtin Nanaimo Fixtures
-------------------------------------------------

A set of predefined :class:`nanaimo.fixtures.Fixture` types that come with nanaimo.


|pytest logo| nanaimo_gather (gather)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. invisible-code-block: python

    import nanaimo.builtin.nanaimo_gather as gather

    assert gather.pytest_nanaimo_fixture_type().get_canonical_name() == "nanaimo_gather"
    assert gather.pytest_nanaimo_fixture_type().get_argument_prefix() == "gather"

.. autoclass:: nanaimo.builtin.nanaimo_gather.Fixture
    :members:
    :show-inheritance:
    :noindex:

|pytest logo| nanaimo_serial_watch (lw)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. invisible-code-block: python

    import nanaimo.builtin.nanaimo_serial_watch as lw

    assert lw.pytest_nanaimo_fixture_type().get_canonical_name() == "nanaimo_serial_watch"
    assert lw.pytest_nanaimo_fixture_type().get_argument_prefix() == "lw"

.. autoclass:: nanaimo.builtin.nanaimo_serial_watch.Fixture
    :members:
    :show-inheritance:
    :noindex:

Fixtures based on :mod:`nanaimo.fixture.SubprocessFixture`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: nanaimo.fixtures.SubprocessFixture
    :members:
    :show-inheritance:
    :noindex:


|pytest logo| nanaimo_cmd (cmd)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. invisible-code-block: python

    import nanaimo.builtin.nanaimo_cmd as cmd

    assert cmd.pytest_nanaimo_fixture_type().get_canonical_name() == "nanaimo_cmd"
    assert cmd.pytest_nanaimo_fixture_type().get_argument_prefix() == "cmd"

.. autoclass:: nanaimo.builtin.nanaimo_cmd.Fixture
    :members:
    :show-inheritance:
    :noindex:


|pytest logo| nanaimo_scp (scp)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. invisible-code-block: python

    import nanaimo.builtin.nanaimo_scp as scp

    assert scp.pytest_nanaimo_fixture_type().get_canonical_name() == "nanaimo_scp"
    assert scp.pytest_nanaimo_fixture_type().get_argument_prefix() == "scp"

.. autoclass:: nanaimo.builtin.nanaimo_scp.Fixture
    :members:
    :show-inheritance:
    :noindex:

|pytest logo| nanaimo_ssh (ssh)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. invisible-code-block: python

    import nanaimo.builtin.nanaimo_ssh as ssh

    assert ssh.pytest_nanaimo_fixture_type().get_canonical_name() == "nanaimo_ssh"
    assert ssh.pytest_nanaimo_fixture_type().get_argument_prefix() == "ssh"

.. autoclass:: nanaimo.builtin.nanaimo_ssh.Fixture
    :members:
    :show-inheritance:
    :noindex:



Instrument Fixtures
-------------------------------------------------

Fixtures for popular measurement, control, and test gear.

|pytest logo| nanaimo_instr_bk_precision (bk)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. invisible-code-block: python

    import nanaimo.instruments.bkprecision as bk

    assert bk.pytest_nanaimo_fixture_type().get_canonical_name() == "nanaimo_instr_bk_precision"
    assert bk.pytest_nanaimo_fixture_type().get_argument_prefix() == "bk"

.. autoclass:: nanaimo.instruments.bkprecision.Series1900BUart
    :members:
    :show-inheritance:
    :noindex:


|pytest logo| nanaimo_instr_ykush (wk)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. invisible-code-block: python

    import nanaimo.instruments.ykush as yk

    assert yk.pytest_nanaimo_fixture_type().get_canonical_name() == "nanaimo_instr_ykush"
    assert yk.pytest_nanaimo_fixture_type().get_argument_prefix() == "yku"

.. autoclass:: nanaimo.instruments.ykush.Fixture
    :members:
    :show-inheritance:
    :noindex:


.. |pytest logo| image:: static/images/pytest1.png
  :width: 100
  :alt: Pytest logo

.. |nanaimo logo| image:: static/images/nanaimo_logo.svg
  :width: 100
  :alt: Nanaimo logo
