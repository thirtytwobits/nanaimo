#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
"""
Also see the YPR class's doctests for nominal case coverage.
"""
import pathlib
import typing

from nanaimo.parsers.imu import YPR


class Handler:
    def __init__(self) -> None:
        self.records = []  # type: typing.List[typing.Tuple[float, float, float]]

    def __call__(self, record: typing.Tuple[float, float, float]) -> None:
        self.records.append(record)


def common_test(binary_data: typing.List[bytes]) -> typing.Tuple[Handler, YPR]:

    handler = Handler()

    parser = YPR(handler)

    for chunk in binary_data:
        parser.push_bytes(chunk)

    return (handler, parser)


def test_line_too_long() -> None:
    '''
    Ensure we discard data if it is too long. This ensures we don't fill available memory up
    with junk data.
    '''
    binary_data = [
        ('a' * (YPR.max_line_length + 1)).encode('ascii'),
        '\n'.encode('ascii')
    ]

    handler, parser = common_test(binary_data)
    assert parser.bytes_discarded == YPR.max_line_length + 1


def test_junk_data() -> None:
    """
    Make sure we continue to parse after encountering unknown data.
    """
    binary_data = [(
        '#YPR=104.65,-3.73,96.25\n' +
        '#YPR=103.87,-3.60,96.24\n' +
        '#YPR=102.71,-3.45,99.21\n' +
        '#YPR=101.29,-3.39,99.14\n' +
        '#YPR=this is a malformed field\n'
        '#YPR=97.29,-2.89,99.08\n' +
        '#YPR=97.26,-3.72,97.16\n' +
        '#YPR=97.99,-3.98,96.61\n'
    ).encode('ascii')]

    handler, parser = common_test(binary_data)
    assert parser.line_errors == 1
    assert len(handler.records) == 7


def test_integers() -> None:
    """
    We do allow integers in our data.
    """
    binary_data = [(
        '#YPR=1,2,3\n'
    ).encode('ascii')]

    handler, parser = common_test(binary_data)
    assert parser.line_errors == 0
    assert len(handler.records) == 1
    assert handler.records[0][0] == 1
    assert handler.records[0][1] == 2
    assert handler.records[0][2] == 3


def test_bulk_data(paths_for_test: typing.Any) -> None:
    """
    Test handling a larger amount of data.
    """
    handler = Handler()

    parser = YPR(handler)

    with open(str(paths_for_test.imu_text), 'r') as textual_data:
        for line in textual_data:
            parser.push_bytes(line.encode('ascii'))

    assert len(handler.records) == 718

    try:
        import numpy as np
        import matplotlib.pyplot as plt

        ypr_data = np.array(handler.records).astype(np.float)
        Y, P, R = ypr_data[:, 0], ypr_data[:, 1], ypr_data[:, 2]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='rectilinear')
        ax.scatter(Y, range(0, len(Y)), c='brown', s=1, alpha=0.5).set_label('yaw')
        ax = fig.add_subplot(111, projection='rectilinear')
        ax.scatter(P, range(0, len(P)), c='orange', s=1, alpha=0.5).set_label('pitch')
        ax = fig.add_subplot(111, projection='rectilinear')
        ax.scatter(R, range(0, len(R)), c='blue', s=1, alpha=0.5).set_label('roll')

        ax.set_xlabel('deg.')
        ax.set_ylabel('sample')
        legend = ax.legend(loc="lower left", fontsize=8)

        # Thanks stackoverflow!
        # https://stackoverflow.com/questions/24706125/setting-a-fixed-size-for-points-in-legend
        if len(legend.legendHandles) >= 3:
            legend.legendHandles[0]._sizes = [30]
            legend.legendHandles[1]._sizes = [30]
            legend.legendHandles[2]._sizes = [30]

        plt.savefig(str(paths_for_test.build_dir / pathlib.Path('ypr.png')),
                    dpi=128,
                    pad_inches=.5,
                    bbox_inches='tight')

    except ImportError:
        print('Install matplotlib to get a pretty graph in the test output.')
