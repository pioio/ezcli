#!/usr/bin/env python3
import taskcli

from taskcli import task, tt

import importlib.util
import sys

from contextlib import contextmanager

tasks_d2 = tt.include("../dir2/sometasks.py")
tasks_d3 = tt.include("../dir3/sometasks.py")
tasks_d4 = tt.include("../../../../tasks.py")

@task
def t1():
    print("Hello from t1 (dir1)")
    #print()
    #tasks_dir2.st()
    #tasks_dir3.st()


if __name__ == "__main__":
    tt.dispatch()
