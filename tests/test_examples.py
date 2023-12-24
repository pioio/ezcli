import taskcli
from taskcli import arg, task




def test_basic():
    taskcli.utils.reset_tasks()

    @task
    def foo():
        pass

    tasks = taskcli.utils.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].name == "foo"
