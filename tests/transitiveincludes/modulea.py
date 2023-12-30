from taskcli import include, task

from . import moduleb


@task
def task_a():
    pass


include.include(moduleb)
