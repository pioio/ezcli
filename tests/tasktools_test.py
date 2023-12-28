from taskcli import Task, task
from taskcli.listing import list_tasks
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
