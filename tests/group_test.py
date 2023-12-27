from taskcli import Group, task
from . import tools

import taskcli
from taskcli.listing import list_tasks
from .tools import reset_context_before_each_test


def test_groups_basic():
    @task
    def foobar1() -> None:
        pass

    group = taskcli.group.Group("magical tasks")

    @task(group=group)
    def magic() -> None:
        pass

    tasks = tools.include_tasks()
    assert tasks[0].group.name == "default"
    assert tasks[1].group.name == "magical tasks"

    with tools.simple_list_format():
        lines = list_tasks(tasks, verbose=0)

    assert """# default
foobar1
# magical tasks
magic""" in "\n".join(lines)



def test_group_context_manager():
    """Test that default arguments are passed to the task."""

    with Group("bar") as group:

        @task
        def foobar():
            pass

        atask = tools.include_tasks()[0]
        assert atask.group.name == "bar"
        assert atask.group == group
