#!/usr/bin/env python

from typing import Annotated, Type, TypeVar

import taskcli
from run import run
from taskcli import Arg, Group, ann, arg, task

important = Group("Important", desc="Development tasks")
dev = Group("dev", desc="Development tasks")


@task(group=dev,aliases="t")
def test():
    """Run unit tests."""
    run(f"pytest tests/ -vvv {taskcli.extra_args()}")


@task(group=dev)
def nox():
    """Run extensive tests using nox."""
    run("nox")


# TODO: instead of important, use a not-important, and hide them explicitly instead
Paths = arg(list[str], "foobar", default=["src", "tests", "tasks.py"], important=True)


with Group("Hidden Group", hidden=True):

    @task
    def task_in_hidden_group():
        print("hello")


with Group("Hidden Group2", hidden=True):

    @task
    def run_hidden():
        task_in_hidden_group()


DEFAULT_LINT_PATH = "src/"


def _get_lint_paths():
    return taskcli.extra_args() or "src/"


with Group("lint"):

    @task(aliases="r")
    def ruff(paths: Paths):
        """Run ruff linter."""
        path_txt = " ".join(paths)
        run(f"ruff format {path_txt}")
        run(f"ruff check {path_txt} --fix")

    @task(important=True, aliases=("l"))
    def lint(paths: Paths):
        """Run all linting tasks."""
        isort(paths)
        ruff(paths)
        mypy(paths)

    @task
    def mypy(paths: Paths):
        """Detect code issues."""
        paths.pop(paths.index("tasks.py"))
        path_txt = " ".join(paths)
        run(f"mypy {path_txt} --strict")

    @task
    def isort(paths: Paths):
        """Reorder imports, float them to top."""
        path_txt = " ".join(paths)
        run(f"isort {path_txt} --float-to-top")


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


@task
def pc():
    """Run pre-commit hooks."""
    lint()


if __name__ == "__main__":
    taskcli.dispatch()
