from taskcli import include, task

from .subdir import modulec


@task
def task_b():
    pass


include.include(modulec)
