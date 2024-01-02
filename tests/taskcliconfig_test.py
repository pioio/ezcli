from taskcli.taskcliconfig import TaskCLIConfig


def test_basic():
    config = TaskCLIConfig(load_from_env=False)
    assert not config.show_hidden



def test_pretty_print():
    config = TaskCLIConfig(load_from_env=False)
    print(config)

from . import tools

def test_env_vars_override_config():
    content = """
from taskcli import tt, task
tt.config.verbose = 1
print(tt.config.verbose)

@task
def foobar():
    print(tt.config.verbose)
"""


    with tools.create_taskfile(content) as filename:
        stdout, stderr = tools.run_tasks(f"t -f {filename} foobar")
        assert stdout == "1\n1\n"

    with tools.set_env(TASKCLI_CFG_VERBOSE="2"):
        with tools.create_taskfile(content) as filename:
            stdout, stderr = tools.run_tasks(f"t -f {filename} foobar")
            assert stdout == "1\n2\n"

    with tools.set_env(TASKCLI_CFG_VERBOSE=""):
        with tools.create_taskfile(content) as filename:
            stdout, stderr = tools.run_tasks(f"t -f {filename} foobar")
            assert stdout == "1\n1\n", f"stdout: {stdout}\nstderr: {stderr}"