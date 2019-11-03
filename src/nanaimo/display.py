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
import typing

import serial

import nanaimo
import nanaimo.config
import nanaimo.connections


class CharacterDisplay:
    """
    A null display that can be used as a no-op when no display is available and
    is also the common base of all character display objects in Nanimo.

    ``nanaimo.cfg`` configuration ::

        [character_display]
        default_message=This will be displayed when clear is called.

    """

    def __init__(self, args: nanaimo.Namespace) -> None:
        self._default_message = args.character_display_default_message

    def write(self, input_line: str) -> None:
        """
        Write text to the display.
        """
        pass

    def clear(self) -> None:
        """
        Clear the display.
        """
        pass

    def set_default_message(self, message: str) -> None:
        """
        Set the message to display when the screen is cleared.
        """
        self._default_message = message


class CharacterDisplayAdafruitSerialBackpack(CharacterDisplay):
    """
    A character display that uses the
    'Adafruit Serial Backpack command protocol \
    <https://learn.adafruit.com/usb-plus-serial-backpack/command-reference>'_

    ``nanaimo.cfg`` configuration ::

        [character_display]
        serial_port=/dev/your_devices_serial_port

    """

    def __init__(self, args: nanaimo.Namespace) -> None:
        super().__init__(args)
        self._uart = serial.Serial(args.character_display_serial_port)
        self.display_on()

    def write(self, input_line: str) -> None:
        self._uart.write(input_line.encode('ascii'))
        self.go_home()

    def clear(self) -> None:
        self.go_home()
        self._uart.write(b'\xFE\x58')
        self.go_home()
        if self._default_message is not None:
            self.write(self._default_message)
            self.go_home()

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

    def store_splash_screen(self, message: str) -> None:
        self._uart.write(b'\xFE\x40')
        if len(message) > 80:
            message = message[:80]
        if len(message) < 80:
            message = message + (' ' * (80 - len(message)))
        self._uart.write(b'\xFE\x40')
        self._uart.write(message.encode('ascii'))


class CharacterDisplayFactory:
    """
    Constructs a :class:`CharacterDisplay` object based on configuration.
    """

    _singleton = None  # type: typing.Optional[CharacterDisplay]

    @classmethod
    def get_display(cls) -> CharacterDisplay:
        if cls._singleton is None:
            defaults = nanaimo.config.ArgumentDefaults.create_defaults_with_early_rc_config()
            args = nanaimo.Namespace(overrides=defaults)
            try:
                cls._singleton = CharacterDisplayAdafruitSerialBackpack(args)
            except serial.SerialException:
                # No hardware display. Just use the null display.
                cls._singleton = CharacterDisplay(args)
        return cls._singleton
