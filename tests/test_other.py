"""

@task decorated adds the tasks to the module where they are defined.
Since that module is that main module, it has to be excplicitly included in each test.

"""

import re
import sys
from typing import Annotated

import pytest

import taskcli
import taskcli.core
from taskcli.dispatching import dispatch
from taskcli import Group, arg, task
from taskcli.listing import list_tasks
from taskcli.task import Task

from . import tools
from .tools import reset_context_before_each_test


def test_basic2():
    @task
    def foobar1():
        pass

    @task(important=True)
    def foobar2():
        pass

    tasks = tools.include_tasks()

    assert len(tasks) == 2
    assert tasks[0].name == "foobar1"
    assert not tasks[0].important
    assert tasks[1].name == "foobar2"
    assert tasks[1].important


def test_run_default_args_str():
    """Test that default arguments are passed to the task."""

    done: str = ""

    @task
    def foobar(name: str = "xxx") -> None:
        nonlocal done
        done = name

    tools.include_tasks()

    dispatch(argv=["foobar"])
    assert done == "xxx"


@pytest.mark.parametrize("default_arg", [None, 42, "zzz", ["foo", 134], []])
def test_run_default_args(default_arg):
    """Test that default arguments are passed to the task."""

    done: str = ""

    @task
    def foobar(name=default_arg):
        nonlocal done
        done = name

    tools.include_tasks()

    try:
        dispatch(argv=["foobar"])
    except SystemExit:
        pytest.fail("SystemExit should not be raised")
    assert done == default_arg
