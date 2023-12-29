from . import tools
from .tools import reset_context_before_each_test

from taskcli import utils, task
import pytest


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


###

def test_get_all_tasks(capsys):
    assert len(utils.get_all_tasks()) == 0

    @task
    def foobar():
        pass

    assert len(utils.get_all_tasks()) == 0
    tasks = tools.include_tasks()

    assert utils.get_all_tasks() == tasks