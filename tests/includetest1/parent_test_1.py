#!/usr/bin/env python3
import dis
from taskcli import task, include, dispatch

import subdir.tasks as child_tasks
import os

@task
def parent() -> None:
    print("parent: " + os.getcwd())

@task
def child1_via_parent() -> None:
    child_tasks.child1()

@task
def child2_via_parent() -> None:
    child_tasks.child2()

# Yet another result when running chil2 directly

include(child_tasks)


# TODO: include(child_tasks.child1)

if __name__ == "__main__":
    dispatch()
