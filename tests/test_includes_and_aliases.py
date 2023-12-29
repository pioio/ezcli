from os import name
from taskcli import include, task, tt
from .tools import reset_context_before_each_test

def test_include_module_via_groups_with_aliases():
    """Test including a module."""
    # TODO: remove this unit test? replaced with other tests below
    from tests.includesandaliases import modulea
    tt.include(modulea)

    tasks = tt.get_tasks()

    full_names = [t.get_full_task_name() for t in tasks]

    assert "nsA.taska" in full_names, f"Full names: {full_names}"

    assert "nsA.nsB.taskb" in full_names, f"Full names: {full_names}"

    assert "nsA.nsB.taskc" in full_names, f"Full names: {full_names}"


def test_include_module_via_groups_with_aliases_and_import_namespaces():
    # TODO: remove this unit test? replaced with other tests below
    from tests.includesandliases2 import modulea
    tt.include(modulea)

    tasks = tt.get_tasks()

    full_names = [t.get_full_task_name() for t in tasks]

    assert "group_nsA.taska" in full_names, f"Full names: {full_names}"
    assert "group_nsA.include_nsA.taskb1" in full_names, f"Full names: {full_names}"
    assert "group_nsA.include_nsA.group_nsB.taskb2" in full_names, f"Full names: {full_names}"

    assert len(full_names) == 3





def test_simple_include_with_aliases():
    # TODO: remove this unit test? replaced with other tests below
    @task
    def sometask():
        pass

    from tests.includesandliases2 import simpleinclude
    with tt.Group("group1", namespace="group1", alias_namespace="g1") as group1:
        tt.include(simpleinclude)

    tasks = tt.get_tasks()
    tasksdict = tt.get_tasks_dict()
    assert "group1.task1" in tasksdict
    group1task1 = tasksdict["group1.task1"]
    assert "g1t1" in group1task1.get_namespaced_aliases(), "alias namespace from should have been appended to the task's aliases"

    assert "group1.task2" in tasksdict

    # Test that applying namespace grom group works fine
    sometask_ = tasksdict["sometask"]
    assert sometask_.get_full_task_name() == "sometask"
    sometask_.add_namespace_from_group(group1)
    assert sometask_.get_full_task_name() == "group1.sometask"


def test_simple_include_with_aliases_from_a_group():
    """Import to a namespaced group via namespaced include, from a namespaces group"""

    from tests.includesandliases2 import simpleinclude2
    with tt.Group("group1", namespace="group1", alias_namespace="g1") as group1:
        tt.include(simpleinclude2, namespace="namespace1", alias_namespace="ns1")

    tasks = tt.get_tasks()
    tasksdict = {t.name: t for t in tasks}

    assert "group1.namespace1.groupS.task1" in tasksdict
    group1task1 = tasksdict["group1.namespace1.groupS.task1"]
    assert "g1ns1gSt1" in group1task1.get_namespaced_aliases()

    # Task0 is not in the groupS
    assert "group1.namespace1.task0" in tasksdict
    group1task0 = tasksdict["group1.namespace1.task0"]
    assert  "g1ns1t0" in group1task0.get_namespaced_aliases()


def test_include_from_same_module_with_namespace():
    """Important for unit tests"""

    @task
    def foobar():
        pass

    tasks = tt.get_tasks_dict()
    assert len(tasks) == 1, f"tasks: {tasks}"
    assert "foobar" in tasks

    tt.include(foobar, namespace="ns1", alias_namespace="ns1")
    tasks = tt.get_tasks_dict()

    assert len(tasks) == 2, f"tasks: {tasks}"
    t = tasks["ns1.foobar"]

import pytest
from taskcli.task import UserError

def test_include_from_same_module_no_namespace():
    """Important for unit tests"""

    @task
    def foobar():
        pass

    with pytest.raises(UserError, match="already exists in"):
        tt.include(foobar)

def test_include_from_same_module_groups_no_namespace():
    """Important for unit tests"""

    with tt.Group("group") as group:
        @task
        def foobar():
            pass

    with tt.Group("group2") as group2:
        with pytest.raises(UserError, match="already exists in"):
            tt.include(foobar)

    with tt.Group("group3", namespace="g3") as group3:
        tt.include(foobar)
        tt.get_tasks_dict()["g3.foobar"]


def test_include_from_same_module_no_namespace_but_to_a_group():
    """Important for unit tests"""

    @task
    def foobar():
        pass

    with tt.Group("group", namespace="group", alias_namespace="g") as group:
        tt.include(foobar)
        t = tt.get_tasks_dict()["group.foobar"]
        assert len(t.get_namespaced_aliases()) == 0






def test_include_from_a_group_via_group():
    """If this works within the same module, it will make unit testing incuding easier"""

    with tt.Group("group1", namespace="group1", alias_namespace="g1") as group:
        @task
        def foobar():
            pass

    with tt.Group("group2", namespace="group2", alias_namespace="g2") as group:
        tt.include(foobar)
        t = tt.get_tasks_dict()["group2.group1.foobar"]


def test_include_from_a_group_via_group_with_include_namesapce():
    """If this works within the same module, it will make unit testing incuding easier"""

    with tt.Group("group1", namespace="group1", alias_namespace="g1") as group:
        @task(aliases=["f"])
        def foobar():
            pass

    with tt.Group("group2", namespace="group2", alias_namespace="g2") as group:
        tt.include(foobar, namespace="include1", alias_namespace="i1")
        t = tt.get_tasks_dict()["group2.include1.group1.foobar"]
        assert ["g2i1g1f"] == t.get_namespaced_aliases()


import sys

def test_include_module_from_same_module_raises_without_namespace():
    """Important for unit tests"""

    @task
    def foobar1():
        pass

    @task
    def foobar2():
        pass

    this_module = sys.modules[__name__]

    with pytest.raises(UserError, match="already exists in"):
        tt.include(this_module)


def test_include_module_from_same_module_works_with_include_namespace():
    """Important for unit tests"""

    @task
    def foobar1():
        pass

    @task
    def foobar2():
        pass

    this_module = sys.modules[__name__]

    tt.include(this_module, namespace="ns")




def test_include_task():
    """Ability to include task is important for unit tests - allows us to chain include calls"""
    @task
    def foobar1():
        pass

    assert "foobar1" in tt.get_tasks_dict()
    thetask = tt.get_tasks_dict()["foobar1"]
    include(thetask, namespace="ns")

    tasks = tt.get_tasks_dict()
    assert "ns.foobar1" in tasks
    assert "foobar1" in tasks
    t1 = tasks["ns.foobar1"]
    t2 = tasks["foobar1"]

    assert t1 is not t2
    assert id(t1) != id(t2)


def test_include_task_long_chain():
    @task
    def foobar():
        pass

    include(foobar, namespace="ns1")
    thetask = tt.get_tasks_dict()["ns1.foobar"]

    thetask = tt.get_task("ns1.foobar") # quick test of "get_task()", dont remove

    include(thetask, namespace="ns2")
    thetask = tt.get_tasks_dict()["ns2.ns1.foobar"]


    with tt.Group("group", namespace="group") as group:
        tt.include(thetask)
        t = tt.get_tasks_dict()["group.ns2.ns1.foobar"]

def test_include_by_default_skips_hidden_tasks():
    @task(hidden=True)
    def foobar1():
        pass

    @task(hidden=False)
    def foobar2():
        pass

    this_module = sys.modules[__name__]
    include(this_module, namespace="ns1")

    tasks = tt.get_tasks_dict()
    assert "foobar1" in tasks  # original one
    assert "foobar2" in tasks  # original one
    assert "ns1.foobar1" not in tasks #
    assert "ns1.foobar2" in tasks # include


def test_include_via_custom_filter():
    @task(important=True)
    def foobar1():
        pass

    @task(important=False)
    def foobar2():
        pass

    this_module = sys.modules[__name__]
    include(this_module, namespace="ns1", filter=lambda t: t.important)

    tasks = tt.get_tasks_dict()
    assert "foobar1" in tasks  # original one
    assert "foobar2" in tasks  # original one
    assert "ns1.foobar1" in tasks #
    assert "ns1.foobar2" not in tasks # include