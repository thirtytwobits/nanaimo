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
The parsers for popular data formats used by IMUs.
"""
import codecs
import re
import typing


class YPR:
    """
    Parser for Yaw, Pitch, and Roll data. This is a line-oriented push parser.

    .. invisible-code-block: python

        from nanaimo.parsers.imu import YPR
        import pytest

    .. code-block:: python

        line0 = '#YPR=103.87,-3.60,96.24'

        # In the simplest manifestation, where you already have an ASCII decoded line,
        # you can use the parse_line method without instantiating the parser class.
        result = YPR.parse_line(line0)

    .. invisible-code-block: python

        assert result is not None
        assert result[0] == pytest.approx(103.87)
        assert result[1] == pytest.approx(-3.60)
        assert result[2] == pytest.approx(96.24)

    .. code-block:: python

        # When dealing with binary data...
        binary_data = [
            (
                '06.57,-4.74,94.76\n' +
                '#YPR=104.65,-3.73,96.25\n' +
                '#YPR=103.87,-3.60,96.24\n' +
                '#YPR=102.71,-3.45,99.21\n' +
                '#YPR=101.29,-3.39,99.14\n' +
                '\n' +
                '# This is a comment after a blank line.\n' +
                '#YPR=100.11,-3.44,99.06\n' +
                '#YPR=98.0'
            ).encode('ascii'),

            (
                '5,-2.12,100.53\n' +
                '#YPR=97.29,-2.89,99.08\n' +
                '#YPR=97.26,-3.72,97.16\n' +
                '#YPR=97.99,-3.98,96.61\n' +
                '#YPR=100.11,-4.45,94.76\n' +
                '# Note that this last record must not be handled\n' +
                '# since we cannot know if it was truncated or not\n' +
                '# because the eol character was not found yet.\n' +
                '#YPR=103.62,-5.19,9'
            ).encode('ascii')
        ]

        # ...you'll need a callback like this.
        class Handler:
            '''
            Using a functor works well if you want to accumulate
            records but you can also just use a simple function
            as a callback.
            '''
            def __init__(self):
                self.records = []

            def __call__(self, record):
                self.records.append(record)


        parser = YPR(Handler())

        # This is a fully incremental push parser so you
        # can feed it raw data from a sensor.
        for chunk in binary_data:
            parser.push_bytes(chunk)

    .. invisible-code-block: python

        handler = parser._record_callback

        assert len(handler.records) == 10
        assert parser.line_errors == 0
        assert parser.ignored_lines == 6
        assert parser.bytes_discarded == 0
        assert handler.records[5][0] == pytest.approx(98.05)
        assert handler.records[5][1] == pytest.approx(-2.12)
        assert handler.records[5][2] == pytest.approx(100.53)

    """
    ypr_pattern = re.compile(r'\s*(-?\d+(?:(?<=.)\.\d+|))\s*,?')

    default_line_ending = '\n'

    max_line_length = 254

    def __init__(self,
                 on_record: typing.Callable[[typing.Tuple[float, float, float]], None],
                 line_ending: str = default_line_ending) -> None:
        self._record_callback = on_record
        self.eol = line_ending
        self._line_buffer = ''
        self._decoder = codecs.getincrementaldecoder('ascii')('strict')
        self.reset()

    def reset(self) -> None:
        self.line_errors = 0
        self.ignored_lines = 0
        self.bytes_discarded = 0

    @classmethod
    def parse_line(cls, line: str) -> typing.Optional[typing.Tuple[float, float, float]]:
        if line.startswith('#YPR='):
            matches = cls.ypr_pattern.findall(line[5:])
            if 3 == len(matches):
                return (float(matches[0]), float(matches[1]), float(matches[2]))
            else:
                raise ValueError('Line starting with #YPR= did not conform to the expected structure.')
        return None

    def push_bytes(self, ypr_bytes: bytes) -> None:
        decoded = self._decoder.decode(ypr_bytes)
        decoded_w_buffer = self._line_buffer + decoded
        self._line_buffer = ''
        lines = decoded_w_buffer.split(self.eol)

        if not decoded.endswith(self.eol):
            if len(lines) > 0:
                self._line_buffer = lines[-1]
                lines = lines[:-1]
            else:
                self._line_buffer = decoded

            if len(self._line_buffer) > self.max_line_length:
                # ASCII == 8 bits
                self.bytes_discarded += len(self._line_buffer)
                self._line_buffer = ''

        for line in lines:
            try:
                ypr = self.parse_line(line)
                if ypr is None:
                    self.ignored_lines += 1
                else:
                    self._record_callback(ypr)
            except ValueError:
                self.line_errors += 1
