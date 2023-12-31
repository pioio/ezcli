#!/usr/bin/env python3
import taskcli

from taskcli import task, tt

import importlib.util
import sys

from contextlib import contextmanager

tasks_d1 = tt.include("../dir1/tasks.py")
tasks_d3 = tt.include("../dir3/tasks.py")
from foobar import foo
from submodule import subfoo


@task
def d2t1():
    print("Hello from d2t1")
    foo()

if __name__ == "__main__":
    tt.dispatch()
