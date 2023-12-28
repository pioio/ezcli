import os
import subprocess

import pytest

import taskcli
import taskcli.core
from taskcli import dispatch, task
from taskcli.group import Group
from taskcli.parser import _extract_extra_args
from taskcli.task import Task
from taskcli.taskcli import TaskCLI

from .tools import reset_context_before_each_test


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


def test_extracting_double_hyphen_args():
    args = ["foo", "--", "--baz", "--bar"]
    task_cli = TaskCLI()
    args = _extract_extra_args(args, task_cli)
    assert args == ["foo"]
    assert task_cli.extra_args_list == ["--baz", "--bar"]

    taskcli.core.task_cli = task_cli
    assert taskcli.get_extra_args_list() == ["--baz", "--bar"]
    assert taskcli.get_extra_args() == "--baz --bar"


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
