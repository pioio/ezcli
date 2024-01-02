"""Collection of tests for various odd edge cases when looking for files to include."""


from tempfile import TemporaryDirectory
from requests import get
import taskcli
from . import tools
import pytest

from .tools import reset_context_before_each_test
import os


def test_empty_taskfile_with_no_parent_results_in_error():
    assert not os.path.exists("/tmp/tasks.py")
    with TemporaryDirectory() as tmpdir:
        with tools.change_dir(tmpdir):
            with open("tasks.py", "w") as f:
                f.write("")

            stdout, stderr = tools.run_tasks("t", check=False)
            assert "taskcli: No tasks found in the task files. Looked in:" in stderr, f"{stdout}, {stderr}"



dummy_taskfile = """
from taskcli import task

@task
def foobar():
    pass
"""


def test_empty_taskfile_with_parent_scenario():
    with TemporaryDirectory() as tmpdir:
        with tools.change_dir(tmpdir):
            with open("tasks.py", "w") as f:
                f.write(dummy_taskfile)
            os.mkdir("subdir")
            with tools.change_dir(tmpdir + "/subdir"):
                with open("tasks.py", "w") as f:
                    f.write("")

                stdout, stderr = tools.run_tasks("t", check=False)
                assert "taskcli: No tasks found in the task files. Looked in:" in stderr, f"{stdout}, {stderr}"


                # Now try enabling looking for parent via the empty taskfile.
                with open("tasks.py", "w") as f:
                    f.write("from taskcli import tt\ntt.config.parent = True\n")

                with tools.simple_list_format():
                    stdout, stderr = tools.run_tasks("t", check=False)
                assert stdout == """# default
foobar
"""