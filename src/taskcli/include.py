"""Logic for including tasks from other places."""

import sys

from . import core
from .task import Task, task
from .types import Any, AnyFunction, Module


def include_module(module: Module) -> None:
    """Include all tasks from the specified python module."""
    if not hasattr(module, "decorated_functions"):
        module.decorated_functions = []  # type: ignore[attr-defined]

    for decorated_fun in module.decorated_functions:
        assert isinstance(decorated_fun, Task), f"Expected Task, got {type(decorated_fun)}"
        runtime = core.get_runtime()
        runtime.tasks.append(decorated_fun)


def include_function(function: AnyFunction, **kwargs: Any) -> None:
    """Include a function as a task."""
    fun = function
    module_of_fun = sys.modules[fun.__module__]
    if not hasattr(module_of_fun, "decorated_functions"):
        module_of_fun.decorated_functions = []  # type: ignore[attr-defined]

    found = False
    for atask in module_of_fun.decorated_functions:
        if atask.func == fun:
            found = True
            break
    if not found:
        # function has not been decorated with @task yet, decore it, so that we can include it
        task(fun, **kwargs)
    thetask = module_of_fun.decorated_functions[-1]

    runtime = core.get_runtime()
    runtime.tasks.append(thetask)
