#!/usr/bin/env python3
import taskcli

from taskcli import task, tt

import importlib.util
import sys

from contextlib import contextmanager

from foobar import foo

@task
def d1t1():
    print("Hello from d1t1")
    foo()

tasks_d2 = tt.include("../dir2/tasks.py")
tasks_d3 = tt.include("../dir3/tasks.py")

if __name__ == "__main__":
    tt.dispatch()
