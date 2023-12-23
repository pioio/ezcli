#!/usr/bin/env python
from taskcli import arg
from taskcli import run as invoke
from taskcli import run as taskrun
from taskcli import task

# class Run:
#     def __sub__(self, other) -> None:
#         self.function(other)

#     def function(self, arg):
#         print(arg)
#         import os
#         os.system(arg)

def run(cmd):
    BLUE = "\033[94m"
    END = "\033[0m"
    print(f"{BLUE}@@ {cmd}{END}")
    import os
    os.system(cmd)

def task_lint(func, **kwargs):
    return task(group="lint", **kwargs)(func)

@task_lint
def lint(group="lint", imporant=True):
    isort()
    ruff()

@task_lint
def ruff():
    run("ruff check src/")

@task_lint
def isort():
    run("isort src/ --float-to-top")

@task
def default():
    print("hello")

if __name__ == "__main__":
    taskrun()
