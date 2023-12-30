#!/usr/bin/env python
from subdir import subtasks

from taskcli import task
from taskcli.include import include

include(subtasks)  # should include subtask and subsubtask


@task
def root_task():
    import os

    print("root_task: " + os.getcwd())


if __name__ == "__main__":
    import taskcli

    taskcli.dispatch()
