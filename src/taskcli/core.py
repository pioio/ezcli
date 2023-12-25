import dataclasses
import functools
import inspect
import os
import sys

import taskcli

from .group import Group
from .task import Task, task
from .taskcli import TaskCLI
from .types import Any, AnyFunction, Module

task_cli = TaskCLI()


def extra_args() -> str:
    """Get args passed to the script after "--".  See also extra_args_list()."""
    return " ".join(extra_args_list())


def extra_args_list() -> list[str]:
    """Get args passed to the script after "--".  See also extra_args()."""
    return task_cli.extra_args_list


def include(module: Module | AnyFunction, **kwargs: Any) -> None:
    """Iterate over decorated @task functions in the module."""
    if isinstance(module, Module):
        for decorated_fun in module.decorated_functions:
            assert isinstance(decorated_fun, Task), f"Expected Task, got {type(decorated_fun)}"
            runtime = taskcli.get_runtime()
            runtime.tasks.append(decorated_fun)
    elif inspect.isfunction(module):
        fun = module

        module_of_fun = sys.modules[fun.__module__]
        if not hasattr(module_of_fun, "decorated_functions"):
            module_of_fun.decorated_functions = []

        found = False
        for atask in module_of_fun.decorated_functions:
            if atask.func == fun:
                found = True
                break
        if not found:
            # function has not been decorated with @task yet, decore it, so that we can include it
            task(fun, **kwargs)
        thetask = module_of_fun.decorated_functions[-1]

        runtime = taskcli.get_runtime()
        runtime.tasks.append(thetask)
        return


def includeold(module: Module, change_dir: bool = True, cwd: str = "") -> None:
    """Iterate over functions, functions with decorate @task should be."""

    def change_working_directory(func: AnyFunction, new_cwd: str) -> Any:
        """Change working directory to the directory of the module which defines the task, and then change back.

        A decorator.
        TODO: assign to each task during task creation, not only included tasks.
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cwd = os.getcwd()
            os.chdir(new_cwd)
            try:
                return func(*args, **kwargs)
            finally:
                os.chdir(cwd)

        return wrapper

    for decorated_fun in module.decorated_functions:
        assert isinstance(decorated_fun, Task), f"Expected DecoratedFunction, got {type(decorated_fun)}"
        # Decorate with CWD change
        if change_dir or cwd:
            if not cwd:
                module_which_defines_task_name = decorated_fun.func.__module__
                module_which_defines_task = sys.modules[module_which_defines_task_name]
                cwd = os.path.dirname(inspect.getfile(module_which_defines_task))
            decorated_fun.func = change_working_directory(decorated_fun.func, new_cwd=cwd)

        runtime = taskcli.get_runtime()
        runtime.tasks.append(decorated_fun)
