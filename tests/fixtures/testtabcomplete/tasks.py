#!/usr/bin/env python
from taskcli import task, run_task

@task
def foobar():
    pass


if __name__ == "__main__":
    run_task()