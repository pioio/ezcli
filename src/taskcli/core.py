import dataclasses
import functools
import inspect
import os
import sys

import taskcli
import argparse

from .task import Task
from .group import Group
from .task import Task, task
from .taskcli import TaskCLI
from .types import Any, AnyFunction, Module
from .include import include_module, include_function

task_cli = TaskCLI()


def get_extra_args() -> str:
    """Get args passed to the script after "--". Returns a string. See also extra_args_list()."""
    return " ".join(get_extra_args_list())


def get_extra_args_list() -> list[str]:
    """Get args passed to the script after "--". Returns a list of string. See also extra_args()."""
    return task_cli.extra_args_list


def get_parsed_args() -> argparse.Namespace:
    """Get the result of 'parse_args()' of argparse. Useful for accessing custom arguments if parser was modified."""
    if task_cli.parsed_args is None:
        msg = "Parsed args are available yet. You might be calling this function too early. Did you call dispatch()?"
        raise RuntimeError(msg)
    return task_cli.parsed_args


def include(object: Module | AnyFunction, **kwargs: Any) -> None:
    """Include tasks from the specified object."""
    if isinstance(object, Module):
        include_module(object, **kwargs)
    elif inspect.isfunction(object):
        include_function(object, **kwargs)


def get_runtime() -> "TaskCLI":
    """Return the TaskCLI runtime. It contains the context of the current execution."""
    return taskcli.core.task_cli


def get_tasks() -> list["Task"]:
    """Return the list of all included (known) tasks."""
    return get_runtime().tasks
