"""Tests for testing the listing format of the output of the program.

Tests here do not simplify the formatting of the output.

If default formatting changes, these tests likely have to be updated.
Don't test listing logic here, focus on formatting.
Logic tests should be format agnostic (in other files.)
"""
import re

from taskcli import task
from . import tools
from taskcli.listing import list_tasks
from .tools import reset_context_before_each_test

def test_list_positional_mandatory():
    """Test that positional mandatory arguments are listed"""
    @task
    def foobar(name: int) -> None:
        """This is the first task"""

    tasks = tools.include_tasks()

    lines = list_tasks(tasks, verbose=0)
    assert len(lines) == 1
    assert re.match(r"\* foobar\s+NAME\s+This is the first task", lines[0])

