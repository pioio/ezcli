#!/usr/bin/env python
from asyncio import run_coroutine_threadsafe
from pyclbr import Function
#import parser
from run import run
from taskcli import group
from taskcli import run_task
from taskcli import task
#import taskcli
#import tasks_lint
from taskcli import ann, arg
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
import taskcli

@task(important=True, group="lint")
def lint():
    isort()
    ruff()
    mypy()

DEFAULT_LINT_PATH = "src/"
def _get_lint_paths():
    return taskcli.extra_args() or "src/"

Paths = ann[list[str], arg(nargs="*", default=["x", "z"])]

@task(group="lint")
def ruff(paths:Paths):
    print("ruff", paths)

@task
def argparse():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("foo" ,nargs="*", default=["x", "y"])
    print(parser.parse_args([]))
    print(parser.parse_args(["a", "b"]))

@task(group="lint")
def mypy(*, path="src/"):
    """Detect code issues."""
    run(f"mypy {path} --strict")

@task(group="lint")
def isort(path="src/"):
    """Reorder imports, float them to top."""
    run(f"isort {path} --float-to-top")

@task
def pc():
    """Run pre-commit hooks."""
    lint()


if __name__ == "__main__":
    run_task()
