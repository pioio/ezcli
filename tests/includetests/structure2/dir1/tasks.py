#!/usr/bin/env python3
import os
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

with taskcli.utils.change_dir("/tmp"):
    # relative includes must be relative to module to which we're including NOT to the current working directory
    # so, changing the directory here to temp should not be impacting the tt.include()
    tasks_d3 = tt.include("../dir3/tasks.py")

if __name__ == "__main__":
    tt.main()
