import pytest

from taskcli import task, utils

from . import tools
from .tools import reset_context_before_each_test


def test_get_tasks(capsys):
    with pytest.raises(SystemExit):
        utils.get_tasks()
    assert "No tasks found in the current module" in capsys.readouterr().err

    @task
    def foobar():
        pass

    tasks = utils.get_tasks()

    assert len(tasks) == 1
    assert tasks[0].name == "foobar"


def test_get_tasks_with_current_module(capsys):
    import sys

    this_module = sys.modules[__name__]

    with pytest.raises(SystemExit):
        tasks = utils.get_tasks(this_module)

    @task
    def foobar():
        pass

    tasks = utils.get_tasks(this_module)

    assert len(tasks) == 1
    assert tasks[0].name == "foobar"


@pytest.mark.skip("dummy task from tools decorator gets cleared by reset_context_before_each_test")
def test_get_tasks_includes_included_tasks():
    import taskcli.include

    from .tools import dummy_task_from_tools

    @task
    def dummy_task_from_here():
        pass

    taskcli.include.include(dummy_task_from_tools)

    tasks = utils.get_tasks(also_included=True)
    assert len(tasks) == 2
    assert tasks[0].name == "dummy-task-from-here"
    assert tasks[1].name == "dummy-task-from-tools"

    tasks = utils.get_tasks(also_included=False)
    assert len(tasks) == 1
    assert tasks[0].name == "dummy-task-from-here"


###
def test_get_callers_module():
    def foo():
        return utils.get_callers_module()

    assert foo.__module__ == __name__
