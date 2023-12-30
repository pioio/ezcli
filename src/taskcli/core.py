import argparse
import dataclasses
import functools
import os
import typing

import taskcli

from .group import Group
from .task import task
from .taskcli import TaskCLI

if typing.TYPE_CHECKING:
    from .task import Task


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


if typing.TYPE_CHECKING:
    from .tt import Task


def get_runtime() -> "TaskCLI":
    """Return the TaskCLI runtime. It contains the context of the current execution."""
    return taskcli.core.task_cli


def get_tasks() -> list["Task"]:
    """Return the list of all included (known) tasks."""
    return get_runtime().tasks
