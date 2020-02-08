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
import tempfile
import textwrap
import typing

import nanaimo
import nanaimo.fixtures
import functools


class ProgramUploader(nanaimo.fixtures.SubprocessFixture):
    """
    JLinkExe fixture that loads a given hexfile to a target device.
    """

    fixture_name = 'nanaimo_jlink_upload'
    argument_prefix = 'jlink_up'

    script_template = textwrap.dedent('''
        f
        device {device}
        speed {speed}
        si {serial_interface}
        connect
        hwinfo
        st
        h
        moe
        rx {reset_delay_millis}
        loadfile {hexfile}
        r
        qc
        ''').lstrip()

    @classmethod
    def on_visit_test_arguments(cls, arguments: nanaimo.Arguments) -> None:
        super().on_visit_test_arguments(arguments)
        arguments.add_argument('--exe',
                               default='JLinkExe',
                               help='A path to the jlink commander executable.')
        arguments.add_argument('--hexfile',
                               help='Path to a hex file to upload.')
        arguments.add_argument('--device',
                               help='The target device.')
        arguments.add_argument('--interface-speed-khz',
                               help='The interface speed in kilohertz',
                               default='default')
        arguments.add_argument('--serial-interface',
                               help='The serial interface to use (e.g. swd, jtag)',
                               default='swd')
        arguments.add_argument('--reset-delay-millis',
                               default=400,
                               help='Milliseconds to wait after reset before starting to load the new image.')
        arguments.add_argument('--script',
                               default=None,
                               help=textwrap.dedent('''
                            Path to a jlink script to use. If not provided then an script will be generated using an
                            internal default. The following template parameters are supported but optional:

                                {device}             = The target device.
                                {speed}              = The interface speed in kilohertz
                                {serial_interface}   = The serial interface to use.
                                {reset_delay_millis} = An optional delay to include after reset.
                                {hexfile}            = The hexfile to upload.
                            ''').lstrip())

    def on_construct_command(self, arguments: nanaimo.Namespace, inout_artifacts: nanaimo.Artifacts) -> str:
        """
        Construct a command to upload (aka "flash") a firmware to a target device using Segger's JLink
        Commander program with the assumption that a Segger debug probe like the JLink is attached to the
        system.
        +----------------+---------------------------------------+--------------------------------------------------+
        | **Artifacts**                                                                                             |
        |                                                                                                           |
        +----------------+---------------------------------------+--------------------------------------------------+
        | key            | type                                  | Notes                                            |
        +================+=======================================+==================================================+
        | ``tmpfile``    | Optional[tempfile.NamedTemporaryFile] | A temporary file containing the jlink script to  |
        |                |                                       | execute with expanded template parameters.       |
        +----------------+---------------------------------------+--------------------------------------------------+
        | ``scriptfile`` | Optional[str]                         | A path to a script file used to invoke jlink.    |
        |                |                                       | This file can contain template parameters.       |
        +----------------+---------------------------------------+--------------------------------------------------+

        """
        script_file_path = self.get_arg_covariant(arguments, 'script')
        tmpfile = tempfile.NamedTemporaryFile(mode='w')
        setattr(inout_artifacts, 'tmpfile', tmpfile)

        # without a script, other args are required:
        get_arg_func = functools.partial(self.get_arg_covariant_or_fail, arguments)

        if script_file_path is None:
            # keep around for as long as the command exists.
            setattr(inout_artifacts, 'scriptfile', None)
            template = self.script_template

        else:
            setattr(inout_artifacts, 'scriptfile', script_file_path)
            with open(script_file_path, 'r') as user_script_file:
                template = user_script_file.read()
            get_arg_func = functools.partial(self.get_arg_covariant, arguments)  # don't fail fixture on missing args

        # poor man's templating
        expanded_script_file = template.format(
                hexfile=get_arg_func('hexfile'),
                device=get_arg_func('device'),
                speed=get_arg_func('interface-speed-khz'),
                serial_interface=get_arg_func('serial-interface'),
                reset_delay_millis=str(get_arg_func('reset-delay-millis'))
            )

        with open(tmpfile.name, 'w') as tempfile_handle:
            tempfile_handle.write(expanded_script_file)

        return '{} -CommanderScript {}'.format(self.get_arg_covariant(arguments, 'exe', 'JLinkExe'),
                                               tmpfile.name)


def pytest_nanaimo_fixture_type() -> typing.Type['nanaimo.fixtures.Fixture']:
    return ProgramUploader
