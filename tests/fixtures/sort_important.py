#!/usr/bin/env python

from taskcli import run_task
from taskcli import task
import taskcli

# order is mixed, as we want to test sortking

taskcli.config.sort_important_first
taskcli.config.sort = taskcli.core.ORDER_TYPE_ALPHA

@task
def task4():
    pass

@task
def task3():
    pass

@task
def task1():
    pass

@task(important=True)
def task2():
    pass


if __name__ == "__main__":
    run_task()
