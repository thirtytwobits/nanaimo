############################################
Nanaimo: Hardware-In-the-Loop Unit Testing
############################################

|badge_docs|_ |badge_build|_ |badge_github_license|_ |badge_pypi_support|_ |badge_pypi_version|_ \
|badge_sonarcloud_quality|_ |badge_sonarcloud_coverage|_ |badge_sonarcloud_bugs|_

.. note::
    Nanaimo is alpha software and will remain so until we bump its version to 1.0.0 or greater.
    We will not knowingly break compatibility within a minor revision but we will break compatibility
    a few more times between minor revisions until beta is declared. Because of this you should depend
    on a minor version explicitly. For example ::

        nanaimo ~= 0.1


.. figure:: https://thirtytwobits.github.io/nanaimo/static/images/nanaimo.png
   :alt: A delicious Nanaimo bar

   A delicious Python treat that makes on-target testing sweet and satisfying.

Nanaimo is a set of utilities and plugins designed to enable integration of hardware test apparatuses
with pytest. This can allow on-target tests to run as part of continuous integration pipelines like
`Buildkite`_, `Bamboo`_, or `Jenkins`_.

.. figure:: https://thirtytwobits.github.io/nanaimo/static/images/pifarm.jpeg
   :alt: S32K evaluation boards attached to Raspberry PIs.

   Example of S32K dev boards attached to Raspberry PI CI workers running the `Buildkite`_ agent and using Nanaimo.

Nanaimo is designed to enable testing of software-defined, physical components in isolation to
provide pre-integration verification of software interfaces and behavioral contracts. It adapts
asynchronous control and monitoring of these components to fit familiar testing idioms
(e.g. x-unit testing) using the popular python test framework, `pytest`_.

.. figure:: https://thirtytwobits.github.io/nanaimo/static/images/block.png
   :alt: Block diagram of Nanaimo's relationship to other components of a typical software build and test pipeline.

   Block diagram of Nanaimo's relationship to other components of a typical software build and test pipeline.

Nanaimo is *not* a simulation framework and is not designed to support the complexity of a full hardware-in-the-loop platform.
Instead it's focused on testing small integrations with a few hardware components and instruments using concepts, syntax,
and frameworks familiar to software engineers. Examples of these small integrations might include verifying a SPI driver for a
microcontroller or ensuring the upload time for a serial bootloader meets expected Key-Performance-Indicators (KPIs). To do this
Nanaimo abstractions provide async interfaces to hardware either directly using available communication protocols
(e.g. serial or IP networks) or by invoking a CLI provided by the instrument vendor. Because of this latter use case some
instruments will require additional programs be available in a test environment.

.. figure:: https://thirtytwobits.github.io/nanaimo/static/images/example.png
   :alt: Example scenario using Nanaimo to test an I2C driver for a microcontroller.

   Example scenario using Nanaimo to test an I2C driver for a microcontroller.

This design is an amalgam of the `TLYF`_ (Test Like You Fly) methodology and the `Swiss cheese`_ model of
failure analysis. Specifically; Nanaimo facilitates testing on actual or representative hardware
for the first integration of software into a part or subassembly. Traditionally software engineers were
responsible only for unit-testing and Software-In-the-Loop (SIL) simulation of their code. Nanaimo encourages
software engineers to also provide hardware integration tests by enabling Hardware-In-the-Loop
`continuous-integration <https://en.wikipedia.org/wiki/Continuous_integration>`_ (HIL-CI, perhaps?).

.. figure:: https://thirtytwobits.github.io/nanaimo/static/images/test_triangle.png
   :alt: Hierarchy of system testing.

   Hierarchy of system testing. Nanaimo focuses on part and subassembly testing.

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

.. |badge_build| image:: https://badge.buildkite.com/80558e71a357a16151e4b537bfc19527c9b1ac543975b92ed7.svg
    :alt: Build status
.. _badge_build: https://buildkite.com/friends-of-scott/nanaimo-release

.. |badge_github_license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT license
.. _badge_github_license: https://github.com/thirtytwobits/nanaimo/blob/master/LICENSE.rst

.. |badge_pypi_support| image:: https://img.shields.io/pypi/pyversions/nanaimo.svg
    :alt: Supported Python Versions
.. _badge_pypi_support: https://pypi.org/project/nanaimo/

.. |badge_pypi_version| image:: https://img.shields.io/pypi/v/nanaimo.svg
    :alt: Pypi Release Version
.. _badge_pypi_version: https://pypi.org/project/nanaimo/

.. |badge_sonarcloud_quality| image:: https://sonarcloud.io/api/project_badges/measure?project=thirtytwobits_nanaimo&metric=alert_status
    :alt: Sonarcloud Quality Gate
.. _badge_sonarcloud_quality: https://sonarcloud.io/dashboard?id=thirtytwobits_nanaimo

.. |badge_sonarcloud_coverage| image:: https://sonarcloud.io/api/project_badges/measure?project=thirtytwobits_nanaimo&metric=coverage
    :alt: Sonarcloud coverage
.. _badge_sonarcloud_coverage: https://sonarcloud.io/dashboard?id=thirtytwobits_nanaimo

.. |badge_sonarcloud_bugs| image:: https://sonarcloud.io/api/project_badges/measure?project=thirtytwobits_nanaimo&metric=bugs
    :alt: Sonarcloud bugs
.. _badge_sonarcloud_bugs: https://sonarcloud.io/dashboard?id=thirtytwobits_nanaimo
