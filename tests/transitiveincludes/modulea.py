from taskcli import task, tt


@task
def task_a():
    pass

from . import moduleb
tt.include(moduleb)