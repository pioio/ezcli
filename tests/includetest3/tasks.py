#!/usr/bin/env python
from taskcli import task, include


from subdir import subtasks

include(subtasks) # should include subtask and subsubtask

@task
def root_task():
    import os
    print("root_task: " + os.getcwd())
    pass


if __name__ == "__main__":
    import taskcli
    taskcli.dispatch()