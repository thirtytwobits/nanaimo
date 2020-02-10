#
# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import pathlib
import re
import typing

import pytest

import nanaimo
from nanaimo import assert_success


@pytest.mark.asyncio
@pytest.mark.parametrize('use_internal_template', [True, False])
async def test_jlink_upload(use_internal_template: bool,
                            nanaimo_jlink_upload: nanaimo.fixtures.Fixture,
                            mock_JLinkExe: pathlib.Path,
                            test_build_config_hex: pathlib.Path,
                            test_jlink_template: pathlib.Path) -> None:
    """
        Test using the jlink ProgramUploader fixture.
    """
    test_args = {
        'jlink_up_exe': str(mock_JLinkExe),
        'jlink_up_hexfile': str(test_build_config_hex),
        'jlink_up_device': 'fake'}

    if not use_internal_template:
        test_args['jlink_up_script'] = str(test_jlink_template)
        test_args['jlink_up_device'] = None  # fails unless args are optional with script

    artifacts = assert_success(await nanaimo_jlink_upload.gather(**test_args))

    cmd = artifacts.cmd
    assert cmd is not None
    print(cmd)

    tmpfile = artifacts.tmpfile

    assert tmpfile is not None
    scriptfile = tmpfile.name
    assert pathlib.Path(scriptfile).exists()

    print(scriptfile)

    hexfile_in_script = None  # type: typing.Optional[str]
    with open(scriptfile, 'r') as scriptfile_handle:
        for line in scriptfile_handle:
            matchobj = re.search(r'^loadfile\s+((?:/|\w)+(?:/|[\w\. -])*\.hex)$', line)
            if matchobj:
                hexfile_in_script = matchobj.group(1)
            print(line, end='')

    assert hexfile_in_script is not None
    assert hexfile_in_script == str(test_build_config_hex)
