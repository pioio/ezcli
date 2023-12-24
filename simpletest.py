#!/usr/bin/env python
import taskcli
from taskcli import task, Arg

from typing import Annotated
@task
def foo():
    pass

tasks = taskcli.utils.get_tasks()
print(tasks)