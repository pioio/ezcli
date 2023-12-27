"""Various tools for unit tests"""
import contextlib
import os
import sys

import pytest

import taskcli
from taskcli import Task, task


# as long as this one is imported to a test module, it will be used before each test
@pytest.fixture(autouse=True)
def reset_context_before_each_test() -> None:
    """Reset the entire context of taskcli, run this before each test"""
    print("Resetting tasks")
    taskcli.utils.reset_tasks()
    return None


def include_tasks() -> list[Task]:
    """Goes through the usual process of including tasks.

    Must be called from the module from which we want to include the tasks.
    """

    import inspect

    previous_frame = inspect.currentframe().f_back
    module_from_which_this_function_was_called = inspect.getmodule(previous_frame)

    taskcli.include(module_from_which_this_function_was_called)
    return taskcli.get_runtime().tasks


@contextlib.contextmanager
def simple_list_format():
    """Context manager to change list formatting to a simple one, which is easy to unit test

    Does two things:
    1. Sets the env var to make child processes have simple formatting.
    2. Changes the config of the current runtime, temporarily (so as to not affects other tests).

    This allows us to:
    - keep unit test code simple,
    - experiment with changing formatting at will, without needing to adjust unit tests.
    """
    with set_env(TASKCLI_ADV_OVERRIDE_FORMATTING="true"):
        with _changed_config(taskcli.configuration.apply_simple_formatting):
            yield


@contextlib.contextmanager
def set_env(**kwargs):
    """Context manager to set environment variables"""
    old_env = os.environ.copy()
    os.environ.update(kwargs)
    yield
    os.environ = old_env


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
