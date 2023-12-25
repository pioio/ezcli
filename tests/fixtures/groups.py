#!/usr/bin/env python

from taskcli import dispatch, task, Group

group = Group("foobar")

def task_group(func, **kwargs):
    return task(group=group, **kwargs)(func)


# order is mixed, as we want to test sortking


@task
def task4():
    pass


@task_group
def task3():
    pass


@task_group
def task1():
    pass


@task_group
def task2():
    pass


if __name__ == "__main__":
    dispatch()
