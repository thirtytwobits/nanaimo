#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import configparser
import pathlib

import nanaimo
from nanaimo.config import ArgumentDefaults


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
    assert 'bar' not in child


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

    subject = child.merge(name='subject', merged='yes')  # type: nanaimo.Namespace

    assert 'yes' == subject.oldparent
    assert 'yes' == subject.merged
    assert 'subject' == subject.name


def test_overrides(test_config: pathlib.Path) -> None:
    """
    Verify that we can provide overrides for namespace attributes.
    """
    fake_args = nanaimo.Namespace()
    setattr(fake_args, 'rcfile', str(test_config))
    defaults = ArgumentDefaults()
    subject = nanaimo.Namespace(None, defaults)
    assert 'test_attr_yup' not in subject

    defaults.set_args(fake_args)
    setattr(subject, 'test_attr_nope', 'yup')
    assert subject.test_attr_yup == 'yup'
    assert subject.test_attr_nope == 'yup'


def test_setup_cfg(local_setup_cfg: pathlib.Path) -> None:
    """
    Verify we can embed Nanaimo configuration in a setup.cfg file.
    """

    # Quick self-check since we don't trust ourselves.
    parser = configparser.ConfigParser()
    assert parser.read([str(local_setup_cfg)]) == [str(local_setup_cfg)]
    assert parser['nanaimo']['test_cfg'] == '1'

    fake_args = nanaimo.Namespace()
    setattr(fake_args, 'rcfile', str(local_setup_cfg))
    defaults = ArgumentDefaults(fake_args)
    subject = nanaimo.Namespace(None, defaults)
    assert subject.test_cfg == '2'


def test_setup_cfg_with_merge(local_setup_cfg: pathlib.Path) -> None:
    """
    Make sure merge acts as expected.
    """
    fake_args = nanaimo.Namespace()
    setattr(fake_args, 'rcfile', str(local_setup_cfg))
    defaults = ArgumentDefaults(fake_args)
    subject = nanaimo.Namespace(None, defaults).merge()  # type: nanaimo.Namespace
    assert subject.test_cfg == '2'


def test_setup_cfg_with_none_value(local_setup_cfg: pathlib.Path) -> None:
    """
    Make sure None values are handled properly when looking for overrides.
    """
    fake_args = nanaimo.Namespace()
    setattr(fake_args, 'rcfile', str(local_setup_cfg))
    setattr(fake_args, 'test_cfg', None)
    defaults = ArgumentDefaults(fake_args)
    subject0 = nanaimo.Namespace(fake_args, defaults, allow_none_values=True)
    assert subject0.test_cfg is None
    subject1 = nanaimo.Namespace(fake_args, defaults, allow_none_values=False)
    assert subject1.test_cfg == '2'
