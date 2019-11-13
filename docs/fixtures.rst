.. _fixtures_reference:

############################################
Fixtures Reference
############################################

This page provides a reference for the available fixtures in Nanaimo. While the
:ref:`nanaimo` guide is comprehensive it is useful only if you are writing your
own fixtures. This page provides a more concise reference when writing tests using
only Nanaimo's built-in fixtures and pytest plugins.

Builtin Fixtures |nanaimo logo|
-------------------------------------------------

.. autoclass:: nanaimo.builtin.nanaimo_gather.Fixture
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: nanaimo.builtin.nanaimo_serial_watch.Fixture
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: nanaimo.instruments.bkprecision.Series1900BUart
    :members:
    :show-inheritance:
    :noindex:

Builtin Subprocess Fixtures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: nanaimo.fixtures.SubprocessFixture
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: nanaimo.builtin.nanaimo_cmd.Fixture
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: nanaimo.builtin.nanaimo_scp.Fixture
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: nanaimo.builtin.nanaimo_ssh.Fixture
    :members:
    :show-inheritance:
    :noindex:


|pytest logo| Pytest Plugins
-------------------------------------------------

.. autofunction:: nanaimo.instruments.bkprecision.nanaimo_instr_bk_precision
    :noindex:

.. autofunction:: nanaimo.builtin.nanaimo_gather.nanaimo_gather
    :noindex:

.. autofunction:: nanaimo.builtin.nanaimo_scp.nanaimo_scp
    :noindex:

.. autofunction:: nanaimo.builtin.nanaimo_ssh.nanaimo_ssh
    :noindex:

.. autofunction:: nanaimo.builtin.nanaimo_serial_watch.nanaimo_serial_watch
    :noindex:

.. autofunction:: nanaimo.pytest.plugin.nanaimo_arguments
    :noindex:

.. autofunction:: nanaimo.pytest.plugin.nanaimo_log
    :noindex:

.. autofunction:: nanaimo.pytest.plugin.nanaimo_fixture_manager
    :noindex:

.. |pytest logo| image:: static/images/pytest1.png
  :width: 100
  :alt: Pytest logo

.. |nanaimo logo| image:: static/images/nanaimo_logo.svg
  :width: 100
  :alt: Nanaimo logo
