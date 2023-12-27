import taskcli
from taskcli import Group, Task, task

from . import tools
from .test_including import clean_stdout
from .tools import include_tasks, reset_context_before_each_test

sideeffect = 0


def test_alphanumeric_order():
    """Test that by default important tasks come first, all within alphanumeric order."""

    @task(hidden=True)
    def d_hidden2():
        pass

    @task()
    def c_regular2():
        pass

    @task()
    def a_regular1():
        pass

    @task(important=True)
    def z_imporant2():
        pass

    @task(hidden=True)
    def b_hidden1():
        pass

    @task(important=True)
    def a_imporant1():
        pass

    tasks = include_tasks()
    show_hidden_tasks = 3
    with tools.simple_list_format():
        lines = taskcli.listing.list_tasks(tasks, verbose=show_hidden_tasks)
    linestxt = "\n".join(lines)
    assert (
        linestxt
        == """a-imporant1
z-imporant2
a-regular1
b-hidden1
c-regular2
d-hidden2"""
    ), "important tasks should be first, the rest should come in alphanumeric order"


def test_list_everything_works(capsys):
    """Test that using -L results in listing everything we can list."""

    hidden_group = Group("hidden-group", hidden=True)

    @task()
    def not_hidden_task():
        pass

    @task(hidden=True)
    def hidden_task():
        pass

    @task(group=hidden_group)
    def task_in_hidden_group():
        pass

    include_tasks()

    with tools.simple_list_format():
        taskcli.dispatch(["-L"])

    stdout = capsys.readouterr().out
    clean_stdout(stdout)
    assert (
        stdout
        == """# default
hidden-task
not-hidden-task
# hidden-group
task-in-hidden-group
"""
    )
