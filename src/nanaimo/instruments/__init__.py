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
This module contains control and communication objects for popular instruments
useful to the type of testing Nanaimo is focused on. Where possible these async
interfaces will use pure-python to communicate directly with an instrument
using known protocols and well supported communication busses (e.g. ethernet, uart, or CAN),
however, some instruments will require the installation of a vendor
CLI for the Nanaimo automation to use.

.. Warning::
    Do not merge third-party code into the Nanaimo repo or provide Nanaimo abstractions
    that are incompatible with the licensing of this software.

.. _jlink-example:

.. figure:: https://thirtytwobits.github.io/nanaimo/static/images/jlink_example.png
   :alt: Example block diagram of a Nanaimo instrument using a vendor CLI.

   Example of a Nanaimo Segger JLink instrument using the JLinkExe CLI as a Python
   subprocess.

:numref:`jlink-example` shows the Nanaimo jlink instrument using `Segger's JLink Commander`_
as a subprocess to upload a firmware image to a microcontroller.

.. _`Segger's JLink Commander`: https://www.segger.com/products/debug-probes/j-link/tools/j-link-commander/

"""
