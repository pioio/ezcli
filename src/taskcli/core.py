import argparse
import dataclasses
import functools
import inspect
import os
import sys
import typing

import taskcli

from .group import Group
from .include import include_function, include_module
from .task import task
from .taskcli import TaskCLI
from .types import Any, AnyFunction, Module

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

from . import utils
if typing.TYPE_CHECKING:
    from .tt import Task

def include(object: Module | AnyFunction | "Task",
            to_module:Module|None=None,
            namespace:str="",
            alias_namespace:str="",
            **kwargs: Any) -> list["Task"]:
    """Include tasks from the specified object into the module which calling this function.

    This function is meant to be called directly from a ./tasks.py file.
    """
    if to_module is None:
        to_module = utils.get_callers_module()

    from .tt import Task

    if isinstance(object, Module):
        return include_module(object, to_module=to_module, namespace=namespace, alias_namespace=alias_namespace, **kwargs)
    elif inspect.isfunction(object):
        return [include_function(object, to_module=to_module, namespace=namespace, alias_namespace=alias_namespace, **kwargs)]
    elif isinstance(object, Task):
        from_module:Module = sys.modules[object.func.__module__]
        from .include import _include_task
        return [_include_task(object, from_module=from_module, to_module=to_module, namespace=namespace, alias_namespace=alias_namespace, **kwargs)]
    else:
        msg = f"include(): Unsupported type: {type(object)}"
        raise Exception(msg)


def get_runtime() -> "TaskCLI":
    """Return the TaskCLI runtime. It contains the context of the current execution."""
    return taskcli.core.task_cli


def get_tasks() -> list["Task"]:
    """Return the list of all included (known) tasks."""
    return get_runtime().tasks
