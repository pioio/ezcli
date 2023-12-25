#!/usr/bin/env python

from typing import Annotated, Type, TypeVar

import taskcli
from run import run
from taskcli import Arg, Group, ann, arg, task

dev = Group("dev", desc="Development tasks")
glint = Group("lint", desc="Linting tasks")
glint = Group("lintx", desc="Linting tasks")


with Group("XXXXX"):

    @task
    def foobarxxxxx():
        pass


@task(group=dev)
def test():
    """Run unit tests."""
    run(f"pytest tests/ -vvv {taskcli.extra_args()}")


@task(group=dev)
def nox():
    """Run extensive tests using nox."""
    run("nox")


# TODO: instead of important, use a not-important, and hide them explicitly instead
Paths = arg(list[str], "foobar", default=["src", "tests", "tasks.py"], important=True)


@task(important=True, group=glint)
def lint(paths: Paths):
    isort(paths)
    ruff(paths)
    mypy(paths)


with Group("lintxxx"):

    @task
    def _hidden_task(paths: Paths):
        isort(paths)
        ruff(paths)
        mypy(paths)


DEFAULT_LINT_PATH = "src/"


def _get_lint_paths():
    return taskcli.extra_args() or "src/"


@task(group=glint)
def ruff(paths: Paths):
    path_txt = " ".join(paths)
    run(f"ruff format {path_txt}")
    run(f"ruff check {path_txt} --fix")


@task(group=dev)
def runcompletion():
    run("_ARGCOMPLETE=1 ./tasks.py")


@task
def rufftwice():
    ruff()
    ruff()


@task
def argparse():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("foo", nargs="*", default=["x", "y"])
    print(parser.parse_args([]))
    print(parser.parse_args(["a", "b"]))


@task(group=glint)
def mypy(paths: Paths):
    """Detect code issues."""
    paths.pop(paths.index("tasks.py"))
    path_txt = " ".join(paths)
    run(f"mypy {path_txt} --strict")


@task(group=glint)
def isort(paths: Paths):
    """Reorder imports, float them to top."""
    path_txt = " ".join(paths)
    run(f"isort {path_txt} --float-to-top")


@task
def pc():
    """Run pre-commit hooks."""
    lint()


if __name__ == "__main__":
    taskcli.dispatch()
