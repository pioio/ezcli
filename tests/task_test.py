from xxlimited import foo
from nox import param

import taskcli
import taskcli.core
from taskcli import Group, Task, task

import os
from . import tools
from .tools import reset_context_before_each_test


def test_copy():
    group = Group("foo")

    @task(important=True, aliases=["foo"], group=group)
    def foobar():
        pass

    task1 = tools.include_tasks()[0]

    assert task1.group == group
    task2 = task1.copy(group=group, included_from=None)

    assert task2.group == group
    assert task1 != task2
    assert task1.name == task2.name
    assert task1.important == task2.important
    assert task1.hidden == task2.hidden
    assert task1._aliases == task2._aliases


def test_argparse_names():
    @task
    def foobar(*, foo1, foo2, foo3):
        pass

    task1 = tools.include_tasks()[0]
    para1 = task1.params[0]

    assert para1.get_argparse_names({"-a"}) == ["--foo1", "-f"]
    assert para1.get_argparse_names({"-f"}) == ["--foo1", "-F"]
    assert para1.get_argparse_names({"-f", "-F"}) == ["--foo1"]


def test___call___forwards_call_to_actual_function():

    with tools.change_dir("/tmp"):
        @task
        def foobar(*, foo1):
            return foo1 + 1

        @task
        def pwd():
            return os.getcwd()

        t1 = tools.include_tasks()[0]
        t2 = tools.include_tasks()[1]
        assert (isinstance(t1, Task))
        assert t1(foo1=41) == 42

        assert "/tmp" not in t2()
        assert "taskcli/tests" in t2(), "even though we're in /tmp right now, cwd should be the local checkout"
