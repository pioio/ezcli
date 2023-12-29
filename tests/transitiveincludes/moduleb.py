from taskcli import task, tt

from .subdir import modulec

@task
def task_b():
    pass

tt.include(modulec)
