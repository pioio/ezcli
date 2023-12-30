from taskcli import task, include


@task
def task_a():
    pass

from . import moduleb
include.include(moduleb)