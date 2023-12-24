#!/usr/bin/env python
import dis
from taskcli import task, run_task

@task
def foobar():
    pass


if __name__ == "__main__":
    run_task()