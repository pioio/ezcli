#!/usr/bin/env python
from asyncio import run_coroutine_threadsafe
from os import path
from pyclbr import Function
from typing import Annotated, TypeVar
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
    run(f"pytest tests/ -vvv {taskcli.extra_args()}")

@task
def nox():
    """Run extensive tests using nox"""
    run("nox")


import taskcli
#Paths = ann[list[str], "The paths to lint", arg(nargs="*", default=["global-default"])]
# def xxx(typevar,  help:str|None=None, /, default=["global-default"]):
#     return ann[typevar, help, arg(nargs="*", default=default)]

Paths = arg(list[str], "foobar", default=["global-default"])

@task(important=True, group="lint")
def lint(paths:Paths=["src/"]):
    isort(paths)
    ruff(paths)
    mypy(paths)


DEFAULT_LINT_PATH = "src/"
def _get_lint_paths():
    return taskcli.extra_args() or "src/"

@task(group="lint")
def ruff(paths:Paths):
    path_txt = " ".join(paths)
    run(f"ruff check {path_txt}")

@task
def rufftwice():
    ruff()
    ruff()

@task
def argparse():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("foo" ,nargs="*", default=["x", "y"])
    print(parser.parse_args([]))
    print(parser.parse_args(["a", "b"]))

@task(group="lint")
def mypy(paths:Paths):
    """Detect code issues."""
    path_txt = " ".join(paths)
    run(f"mypy {path_txt} --strict")

@task(group="lint")
def isort(paths:Paths):
    """Reorder imports, float them to top."""
    path_txt = " ".join(paths)
    run(f"isort {path_txt} --float-to-top")

@task
def pc():
    """Run pre-commit hooks."""
    lint()


if __name__ == "__main__":
    run_task()
