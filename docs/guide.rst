.. _guide:

#####################
Using Nanaimo
#####################

To illustrate how to use Nanaimo we are going to work with specific scenario. We'll be writing
tests to verify an I2C driver for a microcontroller

.. figure:: https://thirtytwobits.github.io/nanaimo/static/images/example.png
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
