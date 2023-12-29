from nox import param
import taskcli
import taskcli.core
from taskcli import Group, Task, task

from . import tools
from .tools import reset_context_before_each_test


def test_copy():
    group = Group("foo")

    @task(important=True, aliases=["foo"], group=group)
    def foobar():
        pass

    task1 = tools.include_tasks()[0]

    assert task1.group == group
    task2 = task1.copy(group=group)

    assert task2.group == group
    assert task1 != task2
    assert task1.name == task2.name
    assert task1.important == task2.important
    assert task1.hidden == task2.hidden
    assert task1.aliases == task2.aliases


def test_argparse_names():

    @task
    def foobar(*, foo1, foo2, foo3):
        pass

    task1 = tools.include_tasks()[0]
    para1 = task1.params[0]

    assert para1.get_argparse_names({"-a"}) == ["--foo1", "-f"]
    assert para1.get_argparse_names({"-f"}) == ["--foo1", "-F"]
    assert para1.get_argparse_names({"-f", "-F"}) == ["--foo1"]