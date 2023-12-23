#!/usr/bin/env python

from taskcli import run_task
from taskcli import task


def task_group(func, **kwargs):
    return task(group="foobar", **kwargs)(func)

@task_group
def task1():
    pass

@task_group
def task2():
    pass

@task
def task3():
    pass



if __name__ == "__main__":
    run_task()
