#!/usr/bin/env python
from asyncio import run_coroutine_threadsafe
from pyclbr import Function
from run import run
from taskcli import arg, group
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


# def get_group(group_name, *args):
#     """Create a new group of tasks,

#     support using it as @group and @group(kwarg=3, kwarg=4)
#     """
#     if len(args) == 1 and callable(args[0]):
#         # Decorator is used without arguments
#         return task(group=group_name)(args[0])
#     else:
#         # Decorator is used with arguments
#         def decorator(func, *args, **kwargs):
#             return task(group=group_name, *args, **kwargs)(func)

#         return decorator


# def task_lint(decorated:Function, **kwargs):
#     """Decorator to mark a function as a task."""
#     return task(group="lint", **kwargs)(decorated)


# def task_lint(func, **kwargs):
#     return task(group="lint", **kwargs)(func)


@task(important=True, group="lint")
def lint():
    isort()
    ruff()
    mypy()

DEFAULT_LINT_PATH = "src/"

@task(group="lint")
def ruff(path:str="src/"):
    """Detect code issues."""
    paths = DEFAULT_LINT_PATH or taskcli.args()
    taskcli.args_list
    run(f"ruff check {taskcli.args}")


@task(group="lint")
def mypy(*, path="src/"):
    """Detect code issues."""
    run(f"mypy {path} --strict")

@task(group="lint")
def isort(path="src/"):
    """Reorder imports, float them to top."""
    run(f"isort {path} --float-to-top")

if __name__ == "__main__":
    run_task()
