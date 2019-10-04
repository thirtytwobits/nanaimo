############################################
Nanaimo: Hardware-In-the-Loop Unit Testing
############################################

|badge_docs|_ |badge_build|_ |badge_github_license|_ |badge_pypi_support|_ |badge_pypi_version|_

.. Warning::
    Nanaimo is evolving rapidly right now. It is undergoing a change to focus on pytest
    integration and to introduce its own plugin architecture to allow test apparatuses
    and instruments to be easily contributed.

.. figure:: https://thirtytwobits.github.io/nanaimo/images/nanaimo.png
   :alt: A delicious Nanaimo bar

   A delicious Python treat that makes on-target testing sweet and satisfying.

Nanaimo is a set of utilities and plugins designed to enable real hardware test apparatuses
to be integrated with unit test frameworks like pytest. This can allow on-target tests to
run as part of continuous integration pipelines like `Buildkite`_, `Bamboo`_, or `Jenkins`_.

.. figure:: https://thirtytwobits.github.io/nanaimo/images/pifarm.jpeg
   :alt: S32K eval boards attached to Rasberry PIs.

   Figure 1.0: Example of S32K dev boards attached to Raspberry PI CI workers running the `Buildkite`_ agent and using Nanaimo.

Nanaimo is designed to enable testing of software-defined, physical components in isolation to
provide pre-integration verification of software interfaces and behavioral contracts. It adapts
asynchronous control and monitoring of these components to fit familiar testing idioms
(e.g. x-unit testing) using the popular python test framework, `pytest`_.

.. figure:: https://thirtytwobits.github.io/nanaimo/images/block.png
   :alt: Block diagram of Nanaimo's relationship to other components of a typical software build and test pipeline.

   Figure 1.1: Block diagram of Nanaimo's relationship to other components of a typical software build and test pipeline.

Nanaimo is *not* a simulation framework and is not designed to support the complexity of a full a hardware-in-the-loop
platform. Instead it's focused on testing small integrations with one or two hardware components and instruments.
Examples of this might include verifying a SPI driver for a microcontroller or ensuring a serial bootloader's
upload performance meets expected KPIs. To do this Nanaimo abstractions of instruments provide async interfaces
to hardware either directly using communication busses like serial or ethernet or by invoking a CLI provided by the
instrument vendor. Because of this, some instruments will require additional programs be installed on a system to
work.

.. figure:: https://thirtytwobits.github.io/nanaimo/images/example.png
   :alt: Example scenario using Nanaimo to test an I2C driver for a microcontroller.

   Figure 1.2: Example scenario using Nanaimo to test an I2C driver for a microcontroller.

This design is an amalgam of the `TLYF`_ (Test Like You Fly) methodology and the `Swiss cheese`_ model of
failure analysis. Specifically; the goal is to encourage testing on actual or representative hardware
early in the testing process of a system to make the cheese loaf less hole-y.

.. Note::
    Nanaimo is named after `Nanaimo bars`_ which are about the best things humans have ever invented.

.. _`Nanaimo bars`: https://en.wikipedia.org/wiki/Nanaimo_bar
.. _`Buildkite`: https://buildkite.com
.. _`Bamboo`: https://www.atlassian.com/software/bamboo
.. _`Jenkins`: https://jenkins.io/
.. _`pytest`: https://docs.pytest.org/en/latest/
.. _`TLYF`: https://www.youtube.com/watch?v=0BSaI117ITI
.. _`Swiss cheese`: https://en.wikipedia.org/wiki/Swiss_cheese_model


.. |badge_docs| image:: https://readthedocs.org/projects/nanaimo/badge/?version=latest
    :alt: Documentation Status
.. _badge_docs: https://nanaimo.readthedocs.io/en/latest/?badge=latest

.. |badge_build| image:: https://badge.buildkite.com/0cf50056296ba113958b93f9058aad4cfffb8018062c044bf7.svg
    :alt: Build status
.. _badge_build: https://buildkite.com/friends-of-scott/nanaimo

.. |badge_github_license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT license
.. _badge_github_license: https://github.com/thirtytwobits/nanaimo/blob/master/LICENSE.rst

.. |badge_pypi_support| image:: https://img.shields.io/pypi/pyversions/nanaimo.svg
    :alt: Supported Python Versions
.. _badge_pypi_support: https://pypi.org/project/nanaimo/

.. |badge_pypi_version| image:: https://img.shields.io/pypi/v/nanaimo.svg
    :alt: Pypi Release Version
.. _badge_pypi_version: https://pypi.org/project/nanaimo/
