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


class Fixture(nanaimo.Fixture):
    """
    .. Warning:: Stubbed-out implementation
        This fixture doesn't do anything yet either then the most naive query possible of the Saleae.
        This would be a great first contribution to the Nanaimo project.
    """

    fixture_name = 'saleae'

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--saleae-port',
                               enable_default_from_environ=True,
                               default='10429',
                               help='TCP port for the logic socket server.')
        arguments.add_argument('--saleae-host',
                               enable_default_from_environ=True,
                               default='localhost',
                               help='hostname for the logic socket server.')

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        self.logger.info('about to connect to {}:{}'.format(args.saleae_host, args.saleae_port))
        reader, writer = await asyncio.open_connection(host=args.saleae_host, port=args.saleae_port, loop=self.loop)

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


@nanaimo.PluggyFixtureManager.type_factory
def get_fixture_type() -> typing.Type['nanaimo.Fixture']:
    return Fixture
