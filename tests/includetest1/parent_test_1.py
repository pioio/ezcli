#!/usr/bin/env python3
import dis
import os

import subdir.tasks as child_tasks

from taskcli import dispatch, task
from taskcli.include import include


@task
def parent() -> None:
    print("parent: " + os.getcwd())


@task(change_dir=False)
def parent_no_change_dir() -> None:
    print("parent_no_change: " + os.getcwd())


@task(change_dir=False)
def parent_no_change_dir_to_sibling() -> None:
    parent_sibling()


@task()
def parent_sibling() -> None:
    print("parent_sibling: " + os.getcwd())


@task
def child1_via_parent() -> None:
    child_tasks.child1()


@task
def child2_via_parent() -> None:
    child_tasks.child2()


@task(change_dir=False)
def child1_via_parent_no_change_dir() -> None:
    child_tasks.child1()


@task(change_dir=False)
def child2_via_parent_no_change_dir() -> None:
    child_tasks.child2()


# Yet another result when running chil2 directly

include(child_tasks)

# TODO: include(child_tasks.child1)

if __name__ == "__main__":
    dispatch()
