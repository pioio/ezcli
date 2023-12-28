"""Tests for testing the listing format of the output of the program.

Tests in this module intentionally do not simplify the formatting of the output.

Thus, if the default formatting changes, some tests here likely have to be updated.
Don't test listing logic here, focus on testing formatting.
Any logic tests should be in other test module and be using simplified listing formatting.
"""
import re

from taskcli import task
from taskcli.listing import list_tasks

from . import tools
from .tools import reset_context_before_each_test


def test_list_positional_mandatory():
    """Test that positional mandatory arguments are listed"""

    @task
    def foobar(name: int) -> None:
        """This is the first task"""

    tasks = tools.include_tasks()

    lines = list_tasks(tasks, verbose=0)
    assert len(lines) == 1
    assert re.match(r"foobar\s+NAME\s+This is the first task", lines[0])


def test_formatting():
    """Test without simplifying the formatting of the output.

    This test has to change every time default formatting changes
    """

    stdout, stderr = tools.run_tasks("tests/fixtures/groups.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "default               Default tasks",
        "task4",
        "",
        "foobar",
        "task1",
        "task2",
        "task3",
    ]
