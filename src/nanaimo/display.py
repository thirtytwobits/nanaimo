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
import socket
import textwrap
import typing

import serial

import nanaimo
import nanaimo.config
import nanaimo.connections
import nanaimo.fixtures
import nanaimo.pytest.plugin
import nanaimo.version


class _CharacterDisplayInterface:

    def __init__(self) -> None:
        pass

    def write(self, input_line: typing.Union[typing.List[str], str]) -> None:
        """
        Write text to the display.
        """
        pass

    def clear(self, display_default_message: bool = True) -> None:
        """
        Clear the display.
        """
        pass

    def set_default_message(self, message: str) -> None:
        """
        Set the message to display when the screen is cleared.
        """
        pass

    def set_bg_colour(self, r: int, g: int, b: int) -> None:
        pass

    def configure(self) -> None:
        """
        Configure the display using the arguments provided to this object.
        """
        pass


class _CharacterDisplayAdafruitSerialBackpack(_CharacterDisplayInterface):
    """
    A character display that uses the
    'Adafruit Serial Backpack command protocol \
    <https://learn.adafruit.com/usb-plus-serial-backpack/command-reference>'_

    ``nanaimo.cfg`` configuration ::

        [character_display]
        serial_port=/dev/your_devices_serial_port
        default_message=This is the default message.
        columns=20
        lines=4

    """

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        arguments.add_argument('--serial-port', help='The serial port the character display is attached to.')

    def __init__(self, args: nanaimo.Namespace) -> None:
        port = args.character_display_serial_port
        self._uart = serial.Serial(port)
        self.display_on()
        self._columns = int(args.character_display_columns)
        self._lines = int(args.character_display_lines)
        self._wrapper = textwrap.TextWrapper(width=self._columns, drop_whitespace=True)
        # Enable auto-scroll
        self._uart.write(b'\xFE\x51')
        self._builtin_values = {
            'version': nanaimo.version.__version__,
            'nl': '\n',
            'hostname': socket.gethostname()
        }
        self._default_message = None  # type: typing.Optional[typing.List[str]]
        default_message = args.character_display_default_message
        if default_message is not None:
            self._default_message = default_message.format(**self._builtin_values).split('\n')

    # +-----------------------------------------------------------------------+
    # | CharacterDisplay
    # +-----------------------------------------------------------------------+
    def write(self, input_line: typing.Union[typing.List[str], str]) -> None:
        if not isinstance(input_line, list):
            lines = self._wrapper.wrap(input_line)
        else:
            lines = input_line

        for line_number in range(0, len(lines)):
            self._uart.write(bytes([0xFE, 0x47, 0x01, line_number + 1]))
            self._uart.write(lines[line_number].encode('ascii'))

    def clear(self, display_default_message: bool = True) -> None:
        self._uart.write(b'\xFE\x58')
        if display_default_message and self._default_message is not None:
            self.write(self._default_message)

    # +-----------------------------------------------------------------------+
    # | ADAFRUIT USB+SERIAL LCD BACKPACK
    # |   https://www.adafruit.com/product/781
    # +-----------------------------------------------------------------------+
    def go_home(self) -> None:
        self._uart.write(b'\xFE\x48')

    def display_on(self) -> None:
        self._uart.write(b'\xFE\x42')

    def display_off(self) -> None:
        self._uart.write(b'\xFE\x46')

    def set_bg_colour(self, r: int, g: int, b: int) -> None:
        self._uart.write(bytes([0xFE, 0xD0, r, g, b]))

    def configure(self) -> None:
        self._uart.write(bytes([0xFE, 0xD1, self._columns, self._lines]))
        if self._default_message is not None:
            self._uart.write(bytes([0xFE, 0x40]))
            for line in self._default_message:
                line_len = len(line)
                self._uart.write(line.encode('ascii'))
                if line_len < self._columns:
                    self._uart.write((' ' * (self._columns - line_len)).encode('ascii'))


class CharacterDisplay(nanaimo.fixtures.Fixture):
    """
    A null display that can be used as a no-op when no display is available and
    is also the common base of all character display objects in Nanimo.

    ``nanaimo.cfg`` configuration ::

        [character_display]
        default_message=This will be displayed when clear is called.

    """

    fixture_name = 'character_display'

    @classmethod
    def _create_display(cls, args: typing.Optional[nanaimo.Namespace]) -> _CharacterDisplayInterface:
        if args is None:
            defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()
            args = nanaimo.Namespace(defaults=defaults)
        try:
            return _CharacterDisplayAdafruitSerialBackpack(args)
        except serial.SerialException:
            pass
        # No hardware display. Just use the null display.
        return _CharacterDisplayInterface()

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        _CharacterDisplayAdafruitSerialBackpack.on_visit_test_arguments(arguments)
        arguments.add_argument('--default-message', help='A message to display when the screen is cleared.')
        arguments.add_argument('--columns', default=16, help='The number of characters in a line of text for '
                               'this display.')
        arguments.add_argument('--lines', default=2, help='The number of lines on the display.')
        arguments.add_argument('--write', help='A string to write to the display.')
        arguments.add_argument('--configure', action='store_true', help='Configures the display to use '
                               'configured values (e.g. columns and lines).')
        arguments.add_argument('--clear', action='store_true', help='Clear the screen.')
        arguments.add_argument('--clear-to-default',
                               action='store_true',
                               help='Clear the screen and display the default message.')
        arguments.add_argument('--status',
                               choices=['okay', 'busy', 'fail'],
                               help='Display an overall status for the tests. How this is represented is dependant'
                                    ' on the display.')

    def __init__(self,
                 manager: 'nanaimo.fixtures.FixtureManager',
                 args: typing.Optional[nanaimo.Namespace] = None,
                 **kwargs: typing.Any):
        super().__init__(manager, args, **kwargs)
        self._impl = self._create_display(args)
        self._colour_map = {
            'okay': [0, 255, 0],
            'busy': [0, 0, 255],
            'fail': [255, 0, 0]
        }

    def write(self, input_line: str) -> None:
        """
        Write text to the display.
        """
        try:
            self._impl.write(input_line)
        except serial.SerialException:
            pass

    def clear(self, display_default_message: bool = True) -> None:
        """
        Clear the display.
        """
        try:
            self._impl.clear(display_default_message)
        except serial.SerialException:
            pass

    def configure(self) -> None:
        """
        Configure the display using the arguments provided to this object.
        """
        try:
            self._impl.configure()
        except serial.SerialException:
            pass

    def set_bg_colour(self, r: int, g: int, b: int) -> None:
        try:
            self._impl.set_bg_colour(r, g, b)
        except serial.SerialException:
            pass

    def set_status(self, status: str) -> None:
        status_colour = self._colour_map[status]
        self.set_bg_colour(status_colour[0], status_colour[1], status_colour[2])

    async def on_gather(self, args: nanaimo.Namespace) -> nanaimo.Artifacts:
        if args.character_display_configure:
            self.configure()

        if args.character_display_clear:
            self.clear(display_default_message=False)

        if args.character_display_clear_to_default:
            self.clear(display_default_message=True)

        if args.character_display_write is not None:
            self.write(args.character_display_write)

        if args.character_display_status is not None:
            self.set_status(args.character_display_status)

        return nanaimo.Artifacts()


def pytest_nanaimo_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
    return CharacterDisplay
