"""
Tests for including task from a parent directory.
- combining with existing in the current dir
- there's no local tasks.py file, but there's one in the parent dir

"""

from requests import get
import taskcli
from . import tools
import pytest

from .tools import reset_context_before_each_test
import os

DIR1 = "dir1"  # Has taskfile, task1
DIR2 = "dir1/dir2"
DIR3 = "dir1/dir2/dir3"  # has taskfile, task3
DIR4 = "dir1/dir2/dir3/dir4"
DIR5 = "dir1/dir2/dir3/dir4/dir5" # has taskfile, task5

from taskcli.utils import change_dir

NO_TASKPY = [ DIR2, DIR4 ]
TASKPY = [ DIR1, DIR3, DIR5 ]
@pytest.mark.include()
@pytest.mark.parametrize("dir", [DIR1, DIR2, DIR3, DIR4, DIR5])
def test_examples_run_basic_listing(dir):
    with change_dir(f"tests/includetests/structure3/{dir}"):
        run_tasks("t")

        if dir in [DIR1, DIR3, DIR5]: # only those have actual tasks.py files
            run_tasks("t -f  tasks.py --show-hidden")
        else:
            assert not os.path.exists("tasks.py")


@pytest.mark.include()
@pytest.mark.parametrize("dir", NO_TASKPY)
def test_no_taskfile_means_opening_one_from_parent_and_honoring_the_groups(dir):
    with change_dir(f"tests/includetests/structure3/{dir}"):
        assert not os.path.exists("tasks.py")

        if dir == DIR2:
            assert run_tasks("t") == "# g1\ntask1"
        elif dir == DIR4:
            assert run_tasks("t") == """# g3
task3

# g3and5
task3shared"""

        else:
            msg = f"Unexpected dir, {dir}"
            raise Exception(msg)

@pytest.mark.include()
@pytest.mark.parametrize("dir", [DIR3, DIR4])
def test_including_parent_via_option(dir, capsys):
    """ Both dir3 and dir4 should load dir3/tasks.py (as default) and dir1/tasks.py (as parent)"""
    with change_dir(f"tests/includetests/structure3/{dir}"):
        print("dir=", os.getcwd())
        assert run_tasks("t -vv -p") == """# g3
task3

# g3and5
task3shared

# g1
task1"""


@pytest.mark.include()
@pytest.mark.parametrize("dir", [DIR3, DIR4])
def test_including_parent_via_ttconfig(dir, capsys):
    """dir5 tasks.py sets tt.config.parent = True, so it should load dir3/tasks.py (as default)"""
    with change_dir(f"tests/includetests/structure3/{dir}"):
        print("dir=", os.getcwd())
        assert run_tasks("t -vv -p") == """# g3
task3

# g3and5
task3shared

# g1
task1"""


@pytest.mark.include()
@pytest.mark.parametrize("dir", [DIR5])
def test_including_parent_with_the_same_group_name(dir, capsys):
    """Right now this results in two separate groups with the same name,

    but that's not a problem right now, group names dont need to be unique.
    """
    with change_dir(f"tests/includetests/structure3/{dir}"):
        print("dir=", os.getcwd())

        # no need for -p here, as dir5/tasks.py sets tt.config.parent = True
        assert "tt.config.parent = True" in open("tasks.py").read()
        assert run_tasks("t -vv") == """# g5
task5

# g3and5
task5shared

# g3
task3

# g3and5
task3shared"""


def test_no_crash_when_no_parent_taskspy(capsys):

    assert not os.path.exists("/tasks.py")
    assert not os.path.exists("/tmp/tasks.py")
    dir = "/tmp/taskcli-unit-test-test_no_crash_when_no_parents"
    if not os.path.exists(dir):
        os.mkdir(dir)
    with change_dir(dir):
        if os.path.exists("tasks.py"):
            os.unlink("tasks.py")
        assert run_tasks("t --init").startswith("Created file")
        assert os.path.exists("tasks.py")
        run_tasks("t -p")



# @pytest.mark.include()
# def test_include_parent_via_tt_config_in_taskfile():
#     with change_dir(f"tests/includetests/structure3/{dir}"):
#         pass


@pytest.mark.include()
def run_tasks(command):
    with tools.simple_list_format():
            stdout, _ = tools.run_tasks(command, check=True)
    return stdout.strip()