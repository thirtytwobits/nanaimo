.. _guide:

#####################
Using Nanaimo
#####################

To illustrate how to use Nanaimo we are going to work with specific scenario. We'll be writing
tests to verify an I2C driver for a microcontroller

.. figure:: https://thirtytwobits.github.io/nanaimo/images/example.png
   :alt: Example scenario using Nanaimo to test an I2C driver for a microcontroller.

   Example scenario using Nanaimo to test an I2C driver for a microcontroller.

Our first task is to design the test. For our example we'll use a psedo framework to demonstrate how
a naive test firmware might be written.

.. code-block:: c

    void setup()
    {
        init_swo(1);
        init_i2c();
    }

    void loop()
    {
        SWO.println("**test i2c: start**\r\n")
        I2C.write(0x42, encode("hello world\n", "utf-8"))
        SWO.println("**test i2c: end**\r\n")
        while (1)
        {
            low_power()
        }
    }

Here we have a firmware that prints a "start" and "end" message to the Serial Wire Output between which it sends a string of bytes on
the I2C bus.

Our test will run the following steps:

1. Upload the firmware using the JLink
2. Start monitoring the SWO bus for the expected start and end test strings.
3. Start a capture session with the Saleae.
4. Reset the microcontroller.
5. When the end string is received stop the Saleae capture session.
6. Provide the captured I2C data as structured :class:`nanaimo.Artifacts` for analysis in pytest tests.

.. note::
    TODO: Finish this document.

############################################
Fixture Reference
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

.. autoclass:: nanaimo.builtin.nanaimo_scp.Fixture
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: nanaimo.builtin.nanaimo_ssh.Fixture
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

.. autofunction:: nanaimo.pytest_plugin.nanaimo_arguments
    :noindex:


.. |pytest logo| image:: docs/images/pytest1.png
  :width: 100
  :alt: Pytest logo

.. |nanaimo logo| image:: docs/images/nanaimo_logo.svg
  :width: 100
  :alt: Nanaimo logo
