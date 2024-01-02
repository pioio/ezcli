#!/usr/bin/env python


# iterate over all functions
import os
import taskcli
#import testing
#from docsgenerator import tasks as docgentasks

# with tt.Group("Weather", desc="child import test"):
#from examples.screenshots import tasks as weather_tasks
from taskcli import run, task, tt

important = tt.Group("Important", desc="Development tasks")

tt.config.default_options = ["--no-go-task"]
tt.config.default_options_tt = ["--no-go-task"]
tt.config.print_task_start_message = True
tt.config.run_show_location = True


def clean_env_for_unit_tests():
    """Remove env vars that can mess with unit tests output."""
    os.environ.pop(taskcli.envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.name)

with tt.Group("dev", desc="Development tasks"):

    @task
    def cwd():
        """Print the current working directory."""
        run("pwd")

    @task(aliases="cov")
    def coverage():
        """Compute test coverage."""
        test(extraargs=f"--cov=taskcli --cov-report=html {tt.get_extra_args()}")
        # print summary:
        run("coverage report")

        cwd = os.getcwd()
        report_path = os.path.join(cwd, "htmlcov", "index.html")
        print(f"file://{report_path}")

    @task(env=["FOOBAR"], important=True, aliases="tt")
    def test(extraargs: str = ""):
        """Run unit tests."""
        clean_env_for_unit_tests()
        run(f"pytest {extraargs} tests/ -vvv -n 4 {tt.get_extra_args()} ")

    @task(aliases="t", important=True)
    def test_fast(extraargs: str = ""):
        """Run fast unit tests."""
        clean_env_for_unit_tests()
        run(f"pytest {extraargs} tests/ -vvv -m 'not include' {tt.get_extra_args()} ")

    @task(important=True)
    def nox():
        """Run extensive tests using nox."""
        run("nox")

    @task(hidden=True)
    def nox_special():
        """(test) Run specia tests using nox."""
        run("nox")

    @task(env=["foooo_username", "foooo_password"])
    def nox_speciadddl2(arg: str):
        del arg
        """(test) Run even more special tests using nox."""
        run("nox")

    @task
    def runcompletion():
        run("_ARGCOMPLETE=1 ./tasks.py")


# TODO: instead of important, use a not-important, and hide them explicitly instead
DEF_LINT_PATHS = ["src", "tests", "tasks.py"]
Paths = tt.arg(list[str], "The paths to lint", default=DEF_LINT_PATHS, important=True)


with tt.Group("Testing module"):

    @task
    def testing_foobar() -> int:
        print("testing foobar")
        return 42

    @task
    def print_cwd():
        import os

        print("cwd:", os.getcwd())


with tt.Group("Hidden Group", hidden=True):

    @task
    def task_in_hidden_group():
        print("hello")

    @task
    def task_in_hidden_group2():
        print("hello")


with tt.Group("HiddenGroup2", hidden=True):

    @task
    def task_in_hidden_group3():
        print("hello")


# >  TODO: fixme
# >  def xxx():
# >      pass
# >  include(xxx)


def _get_lint_paths():
    return tt.get_extra_args() or "src/"


with tt.Group("lints", desc="Code cleanup tasks"):

    @task(important=True, aliases=("l"))
    def lint(paths: Paths = DEF_LINT_PATHS):
        """Run all linting tasks."""
        isort(paths)
        ruff(paths)
        mypy(paths)

    @task(aliases="r")
    def ruff(paths: Paths, example_arg: str = "foobar", example_arg2: str = "foobar"):
        """Run ruff linter."""
        del example_arg
        del example_arg2
        path_txt = " ".join(paths)
        run(f"ruff format {path_txt}")
        run(f"ruff check {path_txt} --fix")

    @task
    def mypy(paths: Paths):
        """Detect code issues."""
        paths.pop(paths.index("tasks.py"))
        paths.pop(paths.index("tests"))
        path_txt = " ".join(paths)
        run(f"mypy {path_txt} --strict")

    @task
    def isort(paths: Paths):
        """Reorder imports, float them to top."""
        path_txt = " ".join(paths)
        run(f"isort {path_txt} --float-to-top")

@task()
def apis():
    """Print the public API of each moduel."""
    import taskcli
    with taskcli.utils.change_dir("src"):
        run("ack -o --python '^(def) [a-zA-Z][a-zA-Z0-9_]*\(' | sort | uniq")

        run("ack -o --python '^(class) [a-zA-Z0-9_]*\(' | sort | uniq")

@task()
def cloc():
    """Count lines of code."""
    import taskcli
    dirs = ["src", "tests", "examples"]
    for dir in dirs:
        run(f"cloc {dir}")
    run(f"cloc {' '.join(dirs)}")



@task
def rufftwice():
    ruff()
    ruff()

with tt.Group("docs"):
    tt.include("docsgenerator/tasks.py", name_namespace="docs", alias_namespace="d")

@task
def argparse():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("foo", nargs="*", default=["x", "y"])
    print(parser.parse_args([]))
    print(parser.parse_args(["a", "b"]))

from docsgenerator import tasks as docgentasks

@task(aliases="pc", important=True)
def pre_commit(*, do_lint: bool = True, do_test: bool = True):
    """Run pre-commit hooks."""
    if do_lint:
        lint()

    if do_test:
        test()

    docgentasks.generate_all_docs()


if __name__ == "__main__":
    tt.dispatch()
