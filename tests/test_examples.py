import taskcli
from taskcli import arg, task
import sys
this_module = sys.modules[__name__]

def test_basic():
    taskcli.utils.reset_tasks()

    @task
    def foo():
        pass

    taskcli.include(this_module)
    tasks = taskcli.utils.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].name == "foo"


def test_basic2():
    taskcli.utils.reset_tasks()

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

