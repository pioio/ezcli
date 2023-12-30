from taskcli import task, include

from .subdir import modulec

@task
def task_b():
    pass

include.include(modulec)
