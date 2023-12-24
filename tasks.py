#!/usr/bin/env python

from run import run
from taskcli import group
import taskcli

from taskcli import task

from taskcli import arg
import taskcli


@task(group='dev')
def foobar():
    print("foobar!")


@task(group='dev')
def test():
    run(f"pytest tests/ -vvv {taskcli.extra_args()}")

@task(group='dev')
def nox():
    """Run extensive tests using nox"""
    run("nox")


# TODO: instead of important, use a not-important, and hide them explicitly instead
Paths = arg(list[str], "foobar", default=["src", "tests"], important=True)

@task(important=True, group="lint")
def lint(paths:Paths):
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

@task(group='examples')
def example_fun1(arg1:str,very_long_arg_name:str="very long name"):
    pass

@task(important=True, group="examples")
def example_fun2(paths_to_lint:str,very_long_arg_name:str,  arg55:int="czxcd", *, confirm:bool):
    pass

@task(important=True, group="examples")
def example_fun2b(arg1:str,very_long_arg_name:str,  arg55:int="czxcd",*, confirm:bool):
    """This is a very long help message, the args should be in one line"""
    pass


@task(important=True, group="examples")
def example_fun3(arg1:str,very_long_arg_name, arg2, arg3, arg4, arg5="xxx",*, arg55:int,arg6:int=32423423423):
    """Example function."""
    pass

@task(important=True, group="examples")
def example_fun4(arg1:str, arg2, arg3, arg4, arg5, arg6):
    """Too many params for one line."""
    pass


taskcli.hide_group("examples")

if __name__ == "__main__":
    taskcli.dispatch()
