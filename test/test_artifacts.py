#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#
import nanaimo


def test_create_artifacts() -> None:
    """
    Create an orphan Artifacts namespace
    """
    subject = nanaimo.Artifacts()
    assert 'foo' not in subject


def test_missing_artifact() -> None:
    """
    Verified that KeyError is not raised if an undefined artifact is accessed.
    """
    subject = nanaimo.Artifacts()
    assert subject.not_an_artifact is None
    assert 'not_an_artifact' not in subject


def test_result_code() -> None:
    """
    Verifies the properties of the Artifacts result code.
    """
    default_subject = nanaimo.Artifacts()
    assert 0 == int(default_subject)
    subject_1 = nanaimo.Artifacts(1)
    assert 1 == int(subject_1)
    subject_1.result_code = 2
    assert 2 == int(subject_1)
