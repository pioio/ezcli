"""Logic for including tasks from other places."""

import sys
from typing import Callable
from unicodedata import name

from .group import get_current_group
from . import core
from .task import Task, UserError, task
from .types import Any, AnyFunction, Module

import logging
log = logging.getLogger(__name__)

def include_module(from_module: Module, to_module:Module, skip_include_info:bool=False,
                    namespace:str="",
                    alias_namespace:str="",
                    filter:Callable[[Task],bool]=lambda t: not t.hidden,
                    ) -> None:
    """Include all tasks from the specified python module.

    When including the main module, we skip the include info, as then all the
    tasks would be marked as included.
    """
    if not hasattr(from_module, "decorated_functions"):
        from_module.decorated_functions = []  # type: ignore[attr-defined]

    if not hasattr(to_module, "decorated_functions"):
        to_module.decorated_functions = []  # type: ignore[attr-defined]

    # make a copy, as we will the original list in _include_task if from_module==to_module,
    tasks = from_module.decorated_functions[:]
    for task in tasks:
        if not skip_include_info: # otherwise we will filter out the ones included from root module
            if not filter(task):
                continue
        # copy the task to the current module
        _include_task(task=task,from_module=from_module,
                  to_module=to_module,
                    skip_include_info=skip_include_info,
                      namespace=namespace,
                        alias_namespace=alias_namespace)

def include_function(function: AnyFunction,to_module:Module, skip_include_info:bool=False, namespace:str="", alias_namespace:str="", **kwargs: Any) -> None:
    """Include a function as a task."""
    fun = function
    module_of_fun = sys.modules[fun.__module__]
    task:None|Task = None
    for atask in module_of_fun.decorated_functions:
        if atask.func == fun:
            task = atask
            break
    if not task:
        # function has not been decorated with @task yet, decore it, so that we can include it
        #task(fun, **kwargs)
        raise Exception("included function was not decorated with @task")

    _include_task(task=task,from_module=module_of_fun,
                  to_module=to_module,
                    skip_include_info=skip_include_info,
                      namespace=namespace,
                        alias_namespace=alias_namespace,
                          **kwargs)


def _include_task(task:Task, from_module:Module, to_module:Module, skip_include_info:bool=False, namespace:str="", alias_namespace:str="", **kwargs: Any) -> None:
    if not hasattr(from_module, "decorated_functions"):
        from_module.decorated_functions = []  # type: ignore[attr-defined]

    if not hasattr(to_module, "decorated_functions"):
        to_module.decorated_functions = []  # type: ignore[attr-defined]


    assert isinstance(task, Task), f"Expected Task, got {type(task)}"

    if not skip_include_info:
        group = get_current_group()
        copy = task.copy(group=group, included_from=from_module)
        copy.add_namespace_from_group(task.group)
    else:
        # We're including the root module, preserve the group info, otherwise we would move all tasks to 'default'
        group = task.group
        copy = task.copy(group=group, included_from=None)

    if namespace:
        copy.add_namespace(namespace, alias_namespace=alias_namespace)

#    if from_module != to_module:
        # the two module can be one and the same when running 'include' for the go tasks

    existing_tasks = [t for t in to_module.decorated_functions if t.name == copy.name]
    if existing_tasks:
        msg = f"Task '{copy.name}' included from {from_module.__file__} already exists in module {to_module.__file__}."
        raise UserError(msg)

    to_module.decorated_functions.append(copy)
    log.debug(f"include_module(): including task {task.name} from {from_module.__file__} to {to_module.__file__}")


def load_tasks_from_module_to_runtime(module: Module) -> None:
    """Include all tasks from a module to the runtime.

    Should be called after all the include() calls have been makde in tasks.py
    Should be called early from .dispatch().
    """
    if not hasattr(module, "decorated_functions"):
        module.decorated_functions = []  # type: ignore[attr-defined]

    runtime = core.get_runtime()
    if runtime.tasks:
        log.debug("skipping load_tasks_from_module_to_runtime(): task have already been loaded")
        return

    for task in module.decorated_functions:
        log.debug(f"load_tasks_from_module_to_runtime(): including task {task.name} from {module} to runtime")
        runtime.tasks.append(task)