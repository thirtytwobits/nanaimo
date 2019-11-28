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
TODO: See https://github.com/ppannuto/python-saleae/blob/master/saleae/saleae.py for the command
strings. They don't seem to be documented anywhere else.
"""

import asyncio
import typing

import nanaimo
import nanaimo.fixtures
import nanaimo.pytest.plugin


class Fixture(nanaimo.fixtures.Fixture):
    """
    This fixture controls a `Saleae logic analyser <https://www.saleae.com/>`_
    attached to the system via USB.

    .. Warning:: Stubbed-out implementation
        This fixture doesn't do anything yet either then the most naive query possible of the Saleae.
        This would be a great first contribution to the Nanaimo project.
    """

    fixture_name = 'nanaimo_instr_saleae'
    argument_prefix = 'sae'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--port',
                               enable_default_from_environ=True,
                               default='10429',
                               help='TCP port for the logic socket server.')
        arguments.add_argument('--host',
                               enable_default_from_environ=True,
                               default='localhost',
                               help='hostname for the logic socket server.')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        saleae_host = self.get_arg_covariant_or_fail(args, 'saleae_host')
        saleae_port = self.get_arg_covariant_or_fail(args, 'saleae_port')

        self.logger.info('about to connect to {}:{}'.format(saleae_host, saleae_port))
        reader, writer = await asyncio.open_connection(host=saleae_host, port=saleae_port, loop=self.loop)

        writer.write('GET_ALL_SAMPLE_RATES\0'.encode('utf-8'))

        rx_buffer = ''
        while 'ACK' not in rx_buffer:
            rx_bytes = await reader.read(256)
            if rx_bytes is not None:
                rx_text = rx_bytes.decode('utf-8')
                self.logger.debug('rx: %s', rx_text)
                rx_buffer += rx_text
                # this is kind of crap. do way better.
                if 'NAK' == rx_buffer[0:3]:
                    self.logger.error('NAK')
                    break

        writer.close()
        await writer.wait_closed()
        return nanaimo.Artifacts()


def pytest_nanaimo_fixture_type() -> typing.Type['Fixture']:
    return Fixture
