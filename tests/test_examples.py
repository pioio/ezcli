"""

@task decorated adds the tasks to the module where they are defined.
Since that module is that main module, it has to be excplicitly included in each test.

"""

import taskcli
from taskcli import arg, task
import sys
this_module = sys.modules[__name__]

import pytest

@pytest.fixture(autouse=True)
def prepare():
    taskcli.utils.reset_tasks()


def test_basic():
    @task
    def foo():
        pass

    taskcli.include(this_module)
    tasks = taskcli.utils.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].name == "foo"


def test_basic2():
    @task
    def foobar1():
        pass

    @task(important=True)
    def foobar2():
        pass

    taskcli.include(this_module)
    tasks = taskcli.utils.get_tasks()
    assert len(tasks) == 2
    assert tasks[0].name == "foobar1"
    assert not tasks[0].important
    assert tasks[1].name == "foobar2"
    assert tasks[1].important



def test_basic2():
    @task
    def foobar1():
        pass

    @task(important=True)
    def foobar2():
        pass

    taskcli.include(this_module)
    tasks = taskcli.utils.get_tasks()
    assert len(tasks) == 2
    assert tasks[0].name == "foobar1"
    assert not tasks[0].important
    assert tasks[1].name == "foobar2"
    assert tasks[1].important
