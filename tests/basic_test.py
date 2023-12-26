import os
import subprocess

import pytest

import taskcli
from taskcli import dispatch, task
from taskcli.group import Group
from taskcli.parser import _extract_extra_args
from taskcli.task import Task
from taskcli.taskcli import TaskCLI

from .test_examples import prepare


def test_foobar():
    def x(z: int | None | list[str]) -> None:
        pass

    with (
        open("/tmp/foobar", "w") as _,
        open("/tmp/foobar") as _,
    ):
        pass


@pytest.mark.skip("Not implemented yet")
def test_tab_completion():
    import os
    import subprocess

    try:
        os.environ["_ARGCOMPLETE"] = "1"
        os.environ["COMP_LINE"] = "tests/fixtures/testtabcomplete/tasks.py "  # The user's current input
        os.environ["COMP_POINT"] = str(len(os.environ["COMP_LINE"]))  # Cursor position

        # Invoke your script with argcomplete
        # Replace 'yourscript' with the path to your script

        process = subprocess.Popen(
            ["tests/fixtures/testtabcomplete/tasks.py"],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        # Check for specific completions in the output

        # Right now this only tests if code reaches specific point, but not if the completion is actually emitted
        # not sure how to check for that.
        assert stdout.decode() == "Starting completion\n"
    finally:
        del os.environ["_ARGCOMPLETE"]
        del os.environ["COMP_LINE"]
        del os.environ["COMP_POINT"]


def run_tasks(path: str) -> tuple[str, str]:
    process = subprocess.Popen(
        [path],
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode()


def test_basic2():
    stdout, stderr = run_tasks("tests/fixtures/groups.py")
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


def test_sort_important():
    stdout, stderr = run_tasks("tests/fixtures/sort_important.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "* task2",  # marked as important
        "* task1",
        "* task3",
        "* task4",
    ]


def test_extracting_double_hyphen_args():
    args = ["foo", "--", "--baz", "--bar"]
    task_cli = TaskCLI()
    args = _extract_extra_args(args, task_cli)
    assert args == ["foo"]
    assert task_cli.extra_args_list == ["--baz", "--bar"]

    taskcli.core.task_cli = task_cli
    assert taskcli.extra_args_list() == ["--baz", "--bar"]
    assert taskcli.extra_args() == "--baz --bar"


def test_create_groups():
    group = Group("foo")
    group2 = Group("foo2")

    groups = [group, group2]
    assert group in groups

    def x():
        pass

    t1 = Task(x, group=group)
    t2 = Task(x, group=group)
    t3 = Task(x, group=group2)

    groups = taskcli.listing.create_groups([t1, t2, t3], group_order=["default", "foo"])
    assert (len(groups)) == 2


def include_tasks() -> list[Task]:
    """Goes through the usual process of including tasks."""
    import sys

    this_module = sys.modules[__name__]
    taskcli.include(this_module)
    return taskcli.get_runtime().tasks


@pytest.mark.parametrize("value", ["1", "-12", "0", "-0"])
def test_conversion_to_int_works(value):
    @task
    def foo(a: int):
        assert isinstance(a, int)

    include_tasks()
    dispatch(["foo", value])


@pytest.mark.parametrize("value", ["1", "1.9", "0", "-1", "-0.9", "23234234.23234234243"])
def test_conversion_to_float_works(value):
    @task
    def foo(a: float):
        assert isinstance(a, float)

    include_tasks()
    dispatch(["foo", value])


@pytest.mark.parametrize("value", ["foobar"])
def test_conversion_to_float_raises_(value):
    @task
    def foo(a: float):
        assert isinstance(a, float)

    include_tasks()
    with pytest.raises(Exception, match="could not convert string to float"):
        dispatch(["foo", value])


@pytest.mark.skip()
@pytest.mark.parametrize("values", [["1"]])
def test_conversion_to_list_of_ints(values):
    @task
    def foo(args: list[int]):
        for element in args:
            assert isinstance(element, int), f"Expected int, got {type(element)}"

    include_tasks()

    dispatch(["foo", *values])


# @pytest.mark.parametrize("value", ["1", "1.9", "0", "-1", "-0.9", "23234234.23234234243"])
@pytest.mark.skip("TODO: disallow positional bool? or expect it to be a string?")
def test_conversion_to_bool_works():
    @task
    def foo(a: bool):
        assert isinstance(a, bool)

    include_tasks()
    dispatch(["foo", "true"])




