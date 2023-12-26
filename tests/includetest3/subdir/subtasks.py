from taskcli import include, task

from .subsubdir import subsubtasks

include(subsubtasks)  # should also include subsubtask


@task
def subtask():
    import os

    print("subtask: " + os.getcwd())
