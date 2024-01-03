#!/usr/bin/env python

import taskcli
from taskcli import dispatch, task

# order is mixed, as we want to test sortking

taskcli.adv_config.sort = taskcli.listing.ORDER_TYPE_ALPHA


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
