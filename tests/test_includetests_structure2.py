"""Set of tests for testing circular includes
dir1 includes dir2 and dir2
dir2 includes dir1 and dir3
dir3 includes dir1 and dir2

"""

import taskcli
from . import tools
import pytest

from .tools import reset_context_before_each_test
# @pytest.mark.include
# def test_dir_scenario1_including_via_path_works():
#     pass



# scenario2_expected_list_output = """# default
# # default
# d1t1
# d2t2
# d3t3
# """


@pytest.mark.include()
@pytest.mark.parametrize("dir", ["dir1","dir2","dir3"])
def test_from_same_dir___list(dir):
    """3 directoris, we try different ways of starting the script and test the output."""
    with taskcli.utils.change_dir(f"tests/includetests/structure2/{dir}"):
        _common_test_list("t -f tasks.py --show-hidden")
        _common_test_list("t --show-hidden")
        _common_test_list("./tasks.py --show-hidden")
        _common_test_list("python tasks.py --show-hidden")
        _common_test_list(f"python ../{dir}/tasks.py --show-hidden")


        _common_test_list("t -f ../dir1 --show-hidden")
        _common_test_list("t -f ../dir2 --show-hidden")
        _common_test_list("t -f ../dir3 --show-hidden")

        _common_test_list("t -f ../dir1/tasks.py --show-hidden")
        _common_test_list("t -f ../dir2/tasks.py --show-hidden")
        _common_test_list("t -f ../dir3/tasks.py --show-hidden")

        _common_test_list("t -f . --show-hidden")
        _common_test_list("t -f ./ --show-hidden")

import os
@pytest.mark.include()
@pytest.mark.parametrize("dir", ["dir1","dir2","dir3"])
def test_from_parent_dir___list(dir, capsys):
    with taskcli.utils.change_dir("tests/includetests/"):
        print(os.getcwd())
        print (dir)
        _common_test_list(f"t -v -f structure2/{dir}/tasks.py --show-hidden")


@pytest.mark.include()
def test_from_subdir___list():
    with taskcli.utils.change_dir("tests/includetests/structure2/dir2/submodule/subsubmodule"):
        _common_test_list("t -f ../../tasks.py --show-hidden") # in dir2
        _common_test_list("t -f ../../../dir3/tasks.py --show-hidden") # in dir3,
        _common_test_list("../../../dir3/tasks.py --show-hidden") # in dir3,


@pytest.mark.include()
def test_from_subdir___list_unrelated_project_bypassing_taskspy_in_between():
    """In btween the starting dir, and the dir4, there's dir2/tasks.py, which we don't want to include in this case."""
    with taskcli.utils.change_dir("tests/includetests/structure2/dir2/submodule/subsubmodule"):
        command = "t -f ../../../dir4/tasks.py --show-hidden"
        with tools.simple_list_format():
            stdout, _ = tools.run_tasks(command, check=True)
        stdout = stdout.replace(" ^", "")
        assert stdout.strip() == """# default
d4t1
""".strip()


@pytest.mark.include()
def test_from_subdir___list_without_f():
    """This should automatically find and run the tasks.py in one of the parent dirs"""
    with taskcli.utils.change_dir("tests/includetests/structure2/dir2/submodule/subsubmodule"):
        _common_test_list("t --show-hidden") #  This sho

    # this should fail
    with taskcli.utils.change_dir("tests/includetests/structure2/dir2/submodule/subsubmodule"):
        _common_test_list("t --show-hidden") #  This sho


def _common_test_list(command):
        """Shared code for listing tasks and checkint output"""
        with tools.simple_list_format():
            stdout, _ = tools.run_tasks(command, check=True)
        stdout = stdout.replace(" ^", "")
        expected = """# default
d1t1
d2t1
d3t1
"""

        assert stdout.strip() == expected.strip()


@pytest.mark.include()
@pytest.mark.parametrize("dir", ["dir1","dir2","dir3"])
@pytest.mark.parametrize("task", ["d1t1","d2t1","d3t1"])
def test_from_same_dir___run(dir, task):
    with taskcli.utils.change_dir(f"tests/includetests/structure2/{dir}"):
        assert tools.run_tasks(f"t -f tasks.py {task}", check=True)[0] == f"""Hello from {task}\nHello from foo()\n"""
        assert tools.run_tasks(f"t {task}", check=True)[0] == f"""Hello from {task}\nHello from foo()\n"""
        assert tools.run_tasks(f"./tasks.py {task}", check=True)[0] == f"""Hello from {task}\nHello from foo()\n"""


@pytest.mark.include()
@pytest.mark.parametrize("dir", ["dir1","dir2","dir3"])
@pytest.mark.parametrize("task", ["d1t1","d2t1","d3t1"])
def test_from_other_dir___run(dir, task):
    with taskcli.utils.change_dir(f"tests/"):
        prefix = f"includetests/structure2/{dir}/"
        assert tools.run_tasks(f"t -f {prefix}tasks.py {task}", check=True)[0] == f"""Hello from {task}\nHello from foo()\n"""

