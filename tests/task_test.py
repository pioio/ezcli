import taskcli
from taskcli import Group, Task, task

from .basic_test import prepare
from .fixtures.groups import task2


def include_tasks() -> list[Task]:
    """Goes through the usual process of including tasks."""
    import sys

    taskcli.include(sys.modules[__name__])
    return taskcli.get_runtime().tasks


def test_copy():
    group = Group("foo")

    @task(important=True, aliases=["foo"], group=group)
    def foobar():
        pass

    task1 = include_tasks()[0]

    assert task1.group == group
    task2 = task1.copy(group=group)

    assert task2.group == group
    assert task1 != task2
    assert task1.name == task2.name
    assert task1.important == task2.important
    assert task1.hidden == task2.hidden
    assert task1.aliases == task2.aliases
