#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import pytest

import nanaimo


def test_create_orphan() -> None:
    """
    Create an orphan Namespace
    """
    subject = nanaimo.Namespace()
    assert 'foo' not in subject


def test_create_single_parent() -> None:
    """
    Create a namespace with a single parent.
    """
    parent = nanaimo.Namespace()
    setattr(parent, 'foo', 1)
    child = nanaimo.Namespace(parent)
    assert 1 == child.foo
    with pytest.raises(KeyError):
        child.bar


def test_create_grandparent() -> None:
    """
    Create a namespace with a grand parent.
    """
    grandparent = nanaimo.Namespace()
    setattr(grandparent, 'foo', 1)
    setattr(grandparent, 'bar', 8)
    parent = nanaimo.Namespace(grandparent)
    setattr(parent, 'foo', 2)
    child = nanaimo.Namespace(parent)
    assert 2 == child.foo
    assert 8 == child.bar
    assert 1 == grandparent.foo
    assert 8 == child.bar


def test_merge() -> None:
    """
    Verify the merge method of Namespace.
    """
    oldparent = nanaimo.Namespace()
    setattr(oldparent, 'oldparent', 'yes')
    setattr(oldparent, 'name', 'oldparent')

    child = nanaimo.Namespace(oldparent)

    setattr(child, 'name', 'child')

    subject = child.merge(name='subject', merged='yes')

    assert 'yes' == subject.oldparent
    assert 'yes' == subject.merged
    assert 'subject' == subject.name
