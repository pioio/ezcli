"""Various tools for unit tests."""
import contextlib
import inspect
import os
import subprocess
import sys

import pytest

import taskcli
import taskcli.core
from taskcli import Task, task
from taskcli.types import Module

########################################################################################################################
# pytest Fixtures
#
# Fictures with autosuse=True are run before each test,
# but to kick in they must be imported directly (from .tools import fixture_name)


# as long as this one is imported to a test module, it will be used before each test
@pytest.fixture(autouse=True)
def reset_context_before_each_test() -> None:
    """Reset the entire context of taskcli, run this before each test"""
    taskcli.utils.reset_tasks()
    return None


########################################################################################################################
# Other


def include_task() -> Task:
    current_frame = inspect.currentframe()
    assert current_frame is not None
    previous_frame = current_frame.f_back
    module_from_which_this_function_was_called = inspect.getmodule(previous_frame)

    res = include_tasks(module=module_from_which_this_function_was_called)

    assert len(res) == 1, f"Expected to find a single task, but found {len(res)} tasks, names: {[t.name for t in res]}"
    return res[0]


def include_tasks(module: Module | None = None) -> list[Task]:
    """Include the tasks from the current module, and return them. Use alongside reset_context_before_each_test .

    This function must be called directly from the module from which we want to include the tasks.
    As it includes the modules from one stack frame up.

    The module which uses this function MUST also import reset_context_before_each_test
    so that the tasks are reset before each test. Otherwise rerunning this function will just keep addings tasks,
    breaking unit tests.
    """

    import inspect

    if module is None:
        previous_frame = inspect.currentframe().f_back
        module_from_which_this_function_was_called = inspect.getmodule(previous_frame)
    else:
        module_from_which_this_function_was_called = module

    expected_fixture = "reset_context_before_each_test"
    if expected_fixture not in module_from_which_this_function_was_called.__dict__:
        msg = (
            f"The module which uses include_tasks() must also import {expected_fixture} "
            "to reset the list of tasks between each test."
        )
        print("found: " + str(module_from_which_this_function_was_called.__dict__.keys()))
        print(module_from_which_this_function_was_called.__name__)
        raise Exception(msg)

    taskcli.include(module_from_which_this_function_was_called)
    return taskcli.core.get_runtime().tasks


@contextlib.contextmanager
def simple_list_format(kwargs: dict[str, str] | None = None):
    """Context manager to change list formatting to a simple one, which is easy to unit test.

    Does two things:
    1. Sets the env var to make any ./task.py child processes have simple formatting
       (used for tests that run a tasks python script to test things end to tend)
    2. Changes the config of the current runtime, temporarily (so as to not affects other tests).
       (used for tests that run taskcli functions directrly)

    So, a single function that can be used for either type of test.

    Simplifying formatting is useful for unit tests because:
    - keep unit test code simple,
    - allows experimenting with changing formatting, without needing to adjust (most of) unit tests.
      (some unit tests do test formatting itself, and those tests do not use this context manager)
    """
    def_kwargs = {
        "TASKCLI_CFG_SHOW_TAGS":"false"
    }
    if kwargs:
        def_kwargs.update(kwargs)

    with set_env(TASKCLI_ADV_OVERRIDE_FORMATTING="true", **def_kwargs):
        with _changed_config(taskcli.configuration.apply_simple_formatting):
            yield


@contextlib.contextmanager
def set_env(**kwargs):
    """Context manager to set environment variables"""
    old_env = os.environ.copy()
    os.environ.update(kwargs)
    yield
    os.environ = old_env  # noqa: B003


@contextlib.contextmanager
def _changed_config(fun, **kwargs):
    """Context manager to set environment variables"""
    old_config = taskcli.configuration.config
    old_settings = {k: v for k, v in old_config.__dict__.items() if k.startswith("render_")}
    taskcli.configuration.apply_simple_formatting()

    yield
    # restore
    for k, v in old_settings.items():
        setattr(old_config, k, v)



def run_tasks(cmd: str) -> tuple[str, str]:
    print(f"run_tasks: {cmd}")
    process = subprocess.Popen(
        [cmd],
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode()
