#!/usr/bin/env python

from typing import Annotated, Type, TypeVar

import taskcli
from run import run
from taskcli import Arg, ann, arg, group, task


@task(group='dev')
def test():
    """Run unit tests."""
    run(f"pytest tests/ -vvv {taskcli.extra_args()}")

@task(group='dev')
def nox():
    """Run extensive tests using nox."""
    run("nox")


# TODO: instead of important, use a not-important, and hide them explicitly instead
Paths = arg(list[str], "foobar", default=["src", "tests"], important=True)

@task(important=True, group="lint")
def lint(paths:Paths):
    isort(paths)
    ruff(paths)
    mypy(paths)


@task(group="lint")
def _hidden_task(paths:Paths):
    isort(paths)
    ruff(paths)
    mypy(paths)


DEFAULT_LINT_PATH = "src/"
def _get_lint_paths():
    return taskcli.extra_args() or "src/"

@task(group="lint")
def ruff(paths:Paths):
    path_txt = " ".join(paths)
    run(f"ruff format {path_txt}")
    run(f"ruff check {path_txt} --fix")


@task(group="dev")
def runcompletion():
    run(f"_ARGCOMPLETE=1 ./tasks.py")


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
    taskcli.dispatch()
