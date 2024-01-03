import argparse
import sys

import pytest

import taskcli
from taskcli import Task, task

from .tools import include_tasks, reset_context_before_each_test
from . import tools

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

    taskcli.dispatch(["foo"])

    assert capsys.readouterr().out == "\n"


def test_specifying_a_dir_works():
    """-f flag"""
    with taskcli.utils.change_dir("tests/includetests/structure2/"):
        with pytest.raises(Exception, match="Error: Specified file not found"):
            tools.run_tasks("t -f nonexisting/.", check=True)

        tools.run_tasks("t -f dir2/.", check=True)
        tools.run_tasks("t -f dir2/../dir3", check=True)

    with taskcli.utils.change_dir("tests/includetests/structure2/dir2/submodule"):
        tools.run_tasks("t -f ../", check=True)
        tools.run_tasks("t -f ..", check=True)

import os
def test_specifying_many_files_works():
    """-f flag accepts more than file, loading them all"""
    with taskcli.utils.change_dir("tests/includetests/"):
        path1 = "structure2/dir2"
        assert os.path.exists(path1)
        with tools.simple_list_format():
            stdout, stderr = tools.run_tasks(f"t -f {path1}", check=True)
        assert stdout == """# default
d1t1 ^
d2t1
d3t1 ^
"""

        # tools.run_tasks("t -f {path1},structure3/dir1/tasks.py", check=True)
        # assert capsys.readouterr().out == "\n", f"Output: {capsys.readouterr().err}"