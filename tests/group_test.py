from operator import le

import taskcli
from taskcli import Group, task, tt
from taskcli.listing import list_tasks

from . import tools
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
        lines = list_tasks(tasks)

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


def test_group_has_children_works():
    with Group("bar") as group:
        with Group("bar2"):

            @task
            def foobar():
                pass

        @task
        def foobar2():
            pass

    for t in tt.get_tasks():
        assert group
    assert len(tt.get_tasks()) == 2


def test_group_namespace_but_no_alias_names():
    """Test that if group has no alias namespace, the tasks's aliases are not namespaced."""

    @task(aliases=["t1", "t2"])
    def tasknogroup():
        pass

    with Group("bar", namespace="bar") as group:

        @task(aliases=["a1", "a2"])
        def foobar():
            pass

        atask = tt.get_tasks_dict()["bar.foobar"]
        assert atask.group.name == "bar"
        assert atask.group == group
        assert atask.name == "bar.foobar"
        assert atask.aliases == ["a1", "a2"]

    # same behavior when copying
    task_no_group = tt.get_tasks_dict()["tasknogroup"]
    task_no_group.add_namespace_from_group(group)
    assert task_no_group.name == "bar.tasknogroup"
    assert task_no_group.aliases == [
        "t1",
        "t2",
    ], "group has no alias namespace, so task aliases should not be namespaced"


def test_group_namespace_with_alias_names():
    """Test that both namespace and alias namespace are added to the task."""

    @task(aliases=["t1", "t2"])
    def tasknogroup():
        pass

    with Group("bar", namespace="bar", alias_namespace="b") as group:

        @task(aliases=["a1", "a2"])
        def foobar():
            pass

        atask = tt.get_tasks_dict()["bar.foobar"]
        assert atask.group.name == "bar"
        assert atask.group == group
        assert atask.name == "bar.foobar"
        assert atask.aliases == ["ba1", "ba2"]

    # same behavior when copying
    task_no_group = tt.get_tasks_dict()["tasknogroup"]
    task_no_group.add_namespace_from_group(group)
    assert task_no_group._get_full_task_name() == "bar.tasknogroup"
    assert task_no_group.aliases == ["bt1", "bt2"]


def test_group_alias_namespace():
    """If group has only alias namespace, only that should be added to the test."""

    @task(aliases=["t1", "t2"])
    def tasknogroup():
        pass

    with Group("bar", alias_namespace="b") as group:

        @task(aliases=["a1", "a2"])
        def foobar():
            pass

        atask = tt.get_tasks_dict()["foobar"]
        assert atask.group.name == "bar"
        assert atask.group == group
        assert atask.name == "foobar"
        assert atask.aliases == ["ba1", "ba2"]

    # same behavior when copying
    task_no_group = tt.get_tasks_dict()["tasknogroup"]
    task_no_group.add_namespace_from_group(group)
    assert task_no_group.name == "tasknogroup"
    assert task_no_group.aliases == ["bt1", "bt2"]
