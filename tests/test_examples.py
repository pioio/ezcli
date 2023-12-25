"""

@task decorated adds the tasks to the module where they are defined.
Since that module is that main module, it has to be excplicitly included in each test.

"""

import re
import sys

import pytest

import taskcli
from taskcli import task
from taskcli.listing import list_tasks
from taskcli.task import Task

this_module = sys.modules[__name__]


@pytest.fixture(autouse=True)
def prepare() -> None:
    taskcli.utils.reset_tasks()
    return None


def include_tasks() -> list[Task]:
    """Goes through the usual process of including tasks."""
    taskcli.include(this_module)
    return taskcli.get_runtime().tasks


def test_basic():
    @task
    def foo():
        pass

    tasks = include_tasks()
    assert len(tasks) == 1
    assert tasks[0].name == "foo"


def test_basic2():
    @task
    def foobar1():
        pass

    @task(important=True)
    def foobar2():
        pass

    tasks = include_tasks()

    assert len(tasks) == 2
    assert tasks[0].name == "foobar1"
    assert not tasks[0].important
    assert tasks[1].name == "foobar2"
    assert tasks[1].important


def test_list_basic():
    @task
    def foobar1():
        """This is the first task"""

    tasks = include_tasks()
    lines = list_tasks(tasks, verbose=0)
    assert len(lines) == 1
    assert re.match(r"\* foobar1\s+This is the first task", lines[0])


def test_groups_basic():
    @task
    def foobar1() -> None:
        pass

    group  = taskcli.group.Group("magical tasks")
    @task(group=group)
    def magic() -> None:
        pass

    tasks = include_tasks()
    assert tasks[0].group.name == "default"
    assert tasks[1].group.name == "magical tasks"
    lines = list_tasks(tasks, verbose=0)

    assert """*** default  Default tasks
* foobar1

*** magical tasks
* magic""" in "\n".join(lines)


def test_list_positional_mandatory():
    @task
    def foobar(name: int) -> None:
        """This is the first task"""

    tasks = include_tasks()

    lines = list_tasks(tasks, verbose=0)
    assert len(lines) == 1
    assert re.match(r"\* foobar\s+NAME\s+This is the first task", lines[0]), "No arguments lister"


def test_list_short_args_share_line_with_task_with_default():
    @task
    def foobar(paths: list[str] = ["src/"]) -> None:  # noqa:  B006
        """This is the first task"""

    tasks = include_tasks()

    lines = list_tasks(tasks, verbose=0)
    assert len(lines) == 1

    assert re.match(
        r"\* foobar\s+This is the first task", lines[0]
    ), "Since we have a default, we should not see it listed"


def test_list_short_args_share_line_with_task_no_default():
    @task
    def foobar(paths: list[str]) -> None:
        """This is the first task"""

    tasks = include_tasks()

    lines = list_tasks(tasks, verbose=0)
    assert len(lines) == 1

    assert re.match(r"\* foobar\s+PATHS\s+This is the first task", lines[0]), "No default, so it should appear"


def test_run_default_args_str():
    """Test that default arguments are passed to the task."""

    done: str = ""

    @task
    def foobar(name: str = "xxx") -> None:
        nonlocal done
        done = name

    include_tasks()

    taskcli.dispatch(argv=["foobar"])
    assert done == "xxx"


@pytest.mark.parametrize("default_arg", [None, 42, "zzz", ["foo", 134], []])
def test_run_default_args(default_arg):
    """Test that default arguments are passed to the task."""

    done: str = ""

    @task
    def foobar(name=default_arg):
        nonlocal done
        done = name

    include_tasks()

    try:
        taskcli.dispatch(argv=["foobar"])
    except SystemExit:
        pytest.fail("SystemExit should not be raised")
    assert done == default_arg
