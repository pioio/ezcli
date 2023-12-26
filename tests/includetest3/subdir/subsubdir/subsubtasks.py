

from taskcli import task

@task
def subsubtask():
    import os
    print("subsubtask: " + os.getcwd())
    pass