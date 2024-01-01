#!/usr/bin/env python3
import taskcli

from taskcli import task, tt

import importlib.util
import sys

from contextlib import contextmanager


from foobar3 import foo

@task
def d3t1():
    print("Hello from d3t1")
    foo()

tasks_d1 = tt.include("../dir1/tasks.py")

if __name__ == "__main__":
    tt.main()
