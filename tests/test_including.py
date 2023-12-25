########################################################################################################################
import pytest

import taskcli
from taskcli import Task, dispatch, include, task

from .basic_test import run_tasks
from .test_examples import prepare


def test_get_taskfile_dir(prepare):
    @task
    def foob() -> None:
        pass

    t = Task(foob)
    dirpath = t.get_taskfile_dir()
    assert dirpath.startswith("/")
    assert dirpath.endswith("/tests")


def clean_stdout(stdout):
    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    return "\n".join(lines)


def test_include_basic():
    stdout, _ = run_tasks("tests/includetest1/parent_test_1.py")
    stdout = clean_stdout(stdout)

    assert (
        stdout
        == """* child1
* child1-via-parent
* child2
* child2-via-parent
* parent"""
    )


########################################################################################################################
# Here we test that  when calling included task the CWD is changed properly
# Confounders:
# - task can be defined ith, or ithout "change_dir"
# - task can be called directly via task cli, or via the taskfile of the parent which includes it
#   in both cases if @task decorator is there, we want to change the dir if change_dir=True (the default)


def test_include_cwd_change():
    stdout, _ = run_tasks("tests/includetest1/parent_test_1.py parent")
    stdout = clean_stdout(stdout)
    last_two_dirs = stdout.split("/")[-2:]
    assert "/".join(last_two_dirs) == "tests/includetest1"

    assert stdout.strip().endswith("tests/includetest1")
    # this test is ran from above "tests/includetest1", parent1 task should change dir to "tests/includetest1"


def test_include_cwd_change_child1():
    stdout, _ = run_tasks("tests/includetest1/parent_test_1.py child1")
    assert stdout.strip().endswith("tests/includetest1/subdir"), "should have changed dir"


def test_include_cwd_change_child1_via_parent():
    stdout, _ = run_tasks("tests/includetest1/parent_test_1.py child1-via-parent")
    assert stdout.strip().endswith("tests/includetest1/subdir"), "should have changed dir"


# child2 does not change dir upon entering the task
def test_include_cwd_change_child2():
    import os

    cwd = os.getcwd()
    stdout, _ = run_tasks("tests/includetest1/parent_test_1.py child2")
    assert (
        stdout.strip() == f"child2: {cwd}"
    ), "should be whatever is the current directory, as child2 tasks did not change the dir"


def test_include_cwd_change_child2_via_parent():
    stdout, _ = run_tasks("tests/includetest1/parent_test_1.py child2-via-parent")
    assert stdout.strip().endswith(
        "tests/includetest1"
    ), "should be parent's directory, as parent task changed the dir, but child2 task did not"


########################################################################################################################
def test_include_from_subsubdir_works():
    """Test that including a task from a sub-subdir, which is not a python module, works."""
    stdout, _ = run_tasks("tests/includetest1/parent_test_2.py")

    assert stdout.strip() == """* subsubchild"""


def test_including_not_decorated_function(prepare):
    done = 0

    def somefun2():
        nonlocal done
        done = 42

    include(somefun2)

    taskcli.dispatch(["somefun2"])
    assert done == 42


@pytest.mark.skip()
def test_including_not_decorated_function_name_change(prepare):
    done = 0

    def somefun():
        nonlocal done
        done = 42

    include(somefun, name="xxx")

    taskcli.dispatch(["xxx"])
    assert done == 42


def test_including_decorated_function(prepare):
    done = 0

    @task
    def somefun():
        nonlocal done
        done = 42

    include(somefun)

    taskcli.dispatch(["somefun"])
    assert done == 42


def test_double_task_decorator_failes(prepare):
    done = 0

    with pytest.raises(ValueError, match="already decorated"):

        @task
        @task
        def somefun():
            nonlocal done
            done = 42
