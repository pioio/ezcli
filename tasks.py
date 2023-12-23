#!/usr/bin/env python
from asyncio import run_coroutine_threadsafe
from run import run
from taskcli import arg
from taskcli import run_task
from taskcli import task
#import taskcli
#import tasks_lint

#taskcli.include(tasks_lint, "lint")


@task
def default():
    print("hello")

@task
def tests():
    run("pytest tests/ -vvv")

@task
def nox():
    """Run extensive tests using nox"""
    run("nox")

def task_lint(func, **kwargs):
    return task(group="lint", **kwargs)(func)

@task_lint
def lint(group="lint", imporant=True):
    isort()
    ruff()
    mypy()

@task_lint
def ruff():
    """Detect code issues."""
    run("ruff check src/")


@task_lint
def mypy():
    """Detect code issues."""
    run("mypy src/ --strict")

@task_lint
def isort():
    """Reorder imports, float them to top."""
    run("isort src/ --float-to-top")

if __name__ == "__main__":
    run_task()
