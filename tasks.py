#!/usr/bin/env python

# iterate over all functions
import inspect
import sys
from typing import Annotated, Type, TypeVar

import taskcli
import testing
from run import run
from taskcli import Arg, Group, ann, arg, include, task
from tests.includetest2.subdir.subsubdir import tasks as subsubtasks

important = Group("Important", desc="Development tasks")


with Group("dev", desc="Development tasks"):

    @task(aliases="t", env=["FOOBAR"])
    def test():
        """Run unit tests."""
        run(f"pytest tests/ -vvv {taskcli.extra_args()}")

    @task(important=True, format="{name} {clear}{red}(PROD!)")
    def nox():
        """Run extensive tests using nox."""
        run("nox")

    @task(important=True)
    def zox():
        """Run extensive tests using nox."""
        run("nox")

    @task(hidden=True)
    def nox_special():
        """(test) Run specia tests using nox."""
        run("nox")

    @task(env=["foooo_username", "foooo_password"])
    def nox_special2(mandatory_arg: str):
        del mandatory_arg
        """(test) Run even more special tests using nox."""
        run("nox")

    @task
    def runcompletion():
        run("_ARGCOMPLETE=1 ./tasks.py")


# TODO: instead of important, use a not-important, and hide them explicitly instead
Paths = arg(list[str], "The paths to lint", default=["src", "tests", "tasks.py"], important=True)


with Group("Testing module"):
    taskcli.include(testing)

    @task
    def testing_foobar():
        print("testing foobar")


with Group("Hidden Group", hidden=True):

    @task
    def task_in_hidden_group():
        print("hello")


with Group("Hidden Group2", hidden=True):

    @task
    def run_hidden():
        task_in_hidden_group()


DEFAULT_LINT_PATH = "src/"

# >  TODO: fixme
# >  def xxx():
# >      pass
# >  include(xxx)


for name, fun in inspect.getmembers(taskcli.utils, inspect.isfunction):
    include(fun)


def _get_lint_paths():
    return taskcli.extra_args() or "src/"


with Group("lint", desc="Code cleanup tasks") as x:

    @task(aliases="r")
    def ruff(paths: Paths, example_arg: str = "foobar", example_arg2: str = "foobar"):
        """Run ruff linter."""
        del example_arg
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


@task
def rufftwice():
    ruff()
    ruff()


include(subsubtasks)


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
