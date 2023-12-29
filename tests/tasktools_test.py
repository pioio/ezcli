from taskcli import Task, task
from taskcli.listing import list_tasks
from taskcli.taskcliconfig import TaskCLIConfig
from taskcli.taskrendersettings import TaskRenderSettings
from taskcli.tasktools import filter_before_listing

from . import tools
from .tools import reset_context_before_each_test


def test_search_tasks_by_tag_and_search_query():
    @task(tags=["tag2"])
    def foobar():
        pass

    @task
    def abc():
        pass

    @task(tags=["tag1", "tag2"])
    def tagged_task():
        pass

    tasks = tools.include_tasks()

    settings = TaskRenderSettings()
    settings.search = "foobar"
    filter_res = filter_before_listing(tasks=tasks, settings=settings)
    task_names = [task.name for task in filter_res.tasks]
    assert task_names == ["foobar"]

    settings = TaskRenderSettings()
    settings.search = ".*gged"
    settings.tags = ["tag2"]
    filter_res = filter_before_listing(tasks=tasks, settings=settings)
    task_names = [task.name for task in filter_res.tasks]
    assert task_names == ["tagged-task"], print(filter_res.progress)
from taskcli import Task, task, tt
from taskcli.taskrendersettings import new_settings

def test_search_shows_hidden():
    @task(hidden=True)
    def foobar():
        pass

    @task
    def abc():
        pass


    tasksdict = tt.get_tasks_dict()
    tasks = tt.get_tasks()
    assert "foobar" in tasksdict


    default_search_settings = TaskRenderSettings()
    assert default_search_settings.show_hidden_tasks == False

    config = TaskCLIConfig()
    config.search = "foobar"
    custom_render_settings = new_settings(config=config)
    custom_render_settings.show_hidden_tasks = True # should be enabled, due to 'search' being set
    assert custom_render_settings.search == "foobar"

    filter_res = filter_before_listing(tasks=tasks, settings=custom_render_settings)
    task_names = [task.name for task in filter_res.tasks]
    assert task_names == ["foobar"]
