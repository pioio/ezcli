"""Logic for including tasks from other places."""

import sys
from unicodedata import name

from .group import get_current_group
from . import core
from .task import Task, task
from .types import Any, AnyFunction, Module

import logging
log = logging.getLogger(__name__)

def include_module(from_module: Module, to_module:Module, skip_include_info:bool=False,
                    namespace:str="",
                    alias_namespace:str="",
                    ) -> None:
    """Include all tasks from the specified python module.

    When including the main module, we skip the include info, as then all the
    tasks would be marked as included.
    """
    if not hasattr(from_module, "decorated_functions"):
        from_module.decorated_functions = []  # type: ignore[attr-defined]

    if not hasattr(to_module, "decorated_functions"):
        to_module.decorated_functions = []  # type: ignore[attr-defined]

    for task in from_module.decorated_functions:
        # copy the task to the current module
        assert isinstance(task, Task), f"Expected Task, got {type(task)}"


        if not skip_include_info:
            group = get_current_group()
            copy = task.copy(group=group, included_from=from_module)
        else:
            # We're including the root module, preserve the group info, otherwise we would move all tasks to 'default'
            group = task.group
            copy = task.copy(group=group, included_from=None)

        if namespace:
            copy.add_namespace(namespace, alias_namespace=alias_namespace)

        if from_module != to_module:
            # the two module can be one and the same when running 'include' for the go tasks
            to_module.decorated_functions.append(copy)
            log.debug(f"include_module(): including task {task.name} from {from_module.__file__} to {to_module.__file__}")
        #runtime = core.get_runtime()
        #runtime.tasks.append(decorated_fun)


def include_function(function: AnyFunction,to_module:Module, skip_include_info:bool=False, namespace:str="", alias_namespace:str="", **kwargs: Any) -> None:
    """Include a function as a task."""
    fun = function
    module_of_fun = sys.modules[fun.__module__]
    if not hasattr(module_of_fun, "decorated_functions"):
        module_of_fun.decorated_functions = []  # type: ignore[attr-defined]

    if not hasattr(to_module, "decorated_functions"):
        to_module.decorated_functions = []  # type: ignore[attr-defined]

    found = False

    for atask in module_of_fun.decorated_functions:
        if atask.func == fun:
            found = True
            break
    if not found:
        # function has not been decorated with @task yet, decore it, so that we can include it
        task(fun, **kwargs)

    thetask = module_of_fun.decorated_functions[-1]
    if not skip_include_info:
        thetask._included_from = module_of_fun
    if namespace:
        #thetask.namespaces = [namespace] # namesapce? TODO: XXX
        thetask.add_namespace(namespace, alias_namespace=alias_namespace)


    if module_of_fun != to_module:
        # the two module can be one and the same when running 'include' in the function
        # located in the same module as where we're running include
        log.debug(f"include_function(): including task {thetask.name} from {module_of_fun.__file__} to {to_module.__file__}")
        to_module.decorated_functions.append(thetask)
    #runtime = core.get_runtime()
    #runtime.tasks.append(thetask)


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