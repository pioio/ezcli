"""Various tools for unit tests"""
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
