import argparse
import sys

import pytest

import taskcli
from taskcli import Task, task

from .utils import include_tasks, reset_context_before_each_test


def test_print_return_value(capsys):
    """Test that using -P flag before the task name results in printing the return value of the task"""

    @task
    def foo() -> int:
        return 42

    tasks = include_tasks()
    taskcli.dispatch(["-P", "foo"])

    assert capsys.readouterr().out == "42\n"


@pytest.mark.skip("Not sure if needed")
def test_print_return_value_after_task_ame(capsys):
    """Test -P flag after the task name results in printing the return value of the task"""

    @task
    def foo() -> int:
        return 42

    tasks = include_tasks()
    taskcli.dispatch(["foo", "-P"])

    assert capsys.readouterr().out == "42\n"
