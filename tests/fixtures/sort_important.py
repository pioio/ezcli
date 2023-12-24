#!/usr/bin/env python

from taskcli import dispatch
from taskcli import task
import taskcli

# order is mixed, as we want to test sortking

taskcli.config.sort = taskcli.listing.ORDER_TYPE_ALPHA

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
    dispatch()
