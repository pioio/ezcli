import pytest
from taskcli import task, run_task
from taskcli.taskcli import TaskCLI
import subprocess
import os


def test_foobar():
    def x(z:int|None|list[str]):
        pass

    with (
         open("/tmp/foobar", "w") as foobar,
        open("/tmp/foobar", "r") as foobar2,
    ):
        pass


@pytest.mark.skip("Not implemented yet")
def test_tab_completion():
    import os
    import subprocess
    try:
        os.environ["_ARGCOMPLETE"] = "1"
        os.environ['COMP_LINE'] = 'tests/fixtures/testtabcomplete/tasks.py '  # The user's current input
        os.environ['COMP_POINT'] = str(len(os.environ['COMP_LINE']))  # Cursor position

        # Invoke your script with argcomplete
        # Replace 'yourscript' with the path to your script

        process = subprocess.Popen(
            ['tests/fixtures/testtabcomplete/tasks.py'],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        # Check for specific completions in the output
        #completions = stdout.decode().splitlines()

        # Right now this only tests if code reaches specific point, but not if the completion is actually emitted
        # not sure how to check for that.
        assert stdout.decode() == "Starting completion\n"
    finally:
        del os.environ["_ARGCOMPLETE"]
        del os.environ['COMP_LINE']
        del os.environ['COMP_POINT']


def run_tasks(path) -> tuple[str, str]:
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
        "*** default",
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
        "* task2", # marked as important
        "* task1",
        "* task3",
        "* task4",
    ]

import taskcli
from taskcli.core import _extract_extra_args

def test_extracting_double_hyphen_args():
    args = ["foo", "--", "--baz", "--bar"]
    task_cli = TaskCLI()
    args = _extract_extra_args(args, task_cli)
    assert args == ["foo"]
    assert task_cli.extra_args_list == ["--baz", "--bar"]

    taskcli.core.task_cli = task_cli
    assert taskcli.extra_args_list() == ["--baz", "--bar"]
    assert taskcli.extra_args() == "--baz --bar"