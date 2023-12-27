"""Tests that actually run external tasks script to test everything end to end."""
import subprocess
import os

from . import tools


def test_formatting():
    """Test without simplifying the formatting of the output.

    This test has to change every time default formatting changes
    """

    stdout, stderr = tools.run_tasks("tests/fixtures/groups.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "*** default         Default tasks",
        "* task4",
        "",
        "*** foobar",
        "* task1",
        "* task2",
        "* task3",
    ]


def test_groups_are_listed():
    with tools.simple_list_format():
        stdout, stderr = tools.run_tasks("tests/fixtures/groups.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "# default",
        "task4",
        "# foobar",
        "task1",
        "task2",
        "task3",
    ]


def test_sort_important():
    with tools.simple_list_format():
        stdout, stderr = tools.run_tasks("tests/fixtures/sort_important.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "task2",  # marked as important
        "task1",
        "task3",
        "task4",
    ]
