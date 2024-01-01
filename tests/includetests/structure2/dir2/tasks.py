#!/usr/bin/env python3
import taskcli

from taskcli import task, tt

import importlib.util
import sys

from contextlib import contextmanager


from submodule import subfoo
from foobar2 import foo


@task
def d2t1():
    print("Hello from d2t1")
    foo()

tasks_d1 = tt.include("../dir1/tasks.py")
tasks_d3 = tt.include("../dir3/tasks.py")

if __name__ == "__main__":
    taskcli.main()
