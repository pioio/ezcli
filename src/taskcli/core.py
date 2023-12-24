import dataclasses
import functools
import inspect
import os
import sys

import taskcli

from .configuration import config
from .decoratedfunction import Task
from .parser import dispatch
from .task import task
from .taskcli import TaskCLI
from .types import Any, AnyFunction, Module
from .utils import param_to_cli_option

task_cli = TaskCLI()


def extra_args() -> str:
    """Get args passed to the script after "--".  See also extra_args_list()."""
    return " ".join(extra_args_list())


def extra_args_list() -> list[str]:
    """Get args passed to the script after "--".  See also extra_args()."""
    return task_cli.extra_args_list


def include(module: Module, change_dir: bool = True, cwd: str = "") -> None:
    """Iterate over functions, functions with decorate @task should be."""

    def change_working_directory(func: AnyFunction, new_cwd: str) -> Any:
        """Change working directory to the directory of the module which defines the task, and then change back."""

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
