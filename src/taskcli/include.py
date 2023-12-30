"""Logic for including Tasks from other modules."""

import inspect
import logging
import sys
from typing import Callable
from unicodedata import name

from . import core, utils
from .group import get_current_group
from .task import Task, UserError
from .types import Any, AnyFunction, Module

log = logging.getLogger(__name__)


def include(
    object: Module | AnyFunction | "Task",
    /,
    *,
    to_module: Module | None = None,
    namespace: str = "",
    alias_namespace: str = "",
    **kwargs: Any,
) -> list["Task"]:
    """Include Tasks from the specified object into the module which is calling this function. Returns included Tasks.

    This function is meant to be called directly from a ./tasks.py file.
    This function is a convenience wrapper around `include_module()` and `include_function()`.

    For more control, call the lower level `include_module()` or `include_function()` directly.

    Example:
    ```
        # Most basic usage - include tasks defined in an external module
        import mysubmodule
        tt.include(mysubmodule)

        # Most basic usage - include one task
        import mysubmodule
        tt.include(mysubmodule.mytask)

        # Include a module or function, and prefix them with a namespace afterwards
        import mysubmodule
        tt.include(mysubmodule, namespace="mysubmodule", alias_namespace="s")

        # Include tasks selectively, based on custom criteria (e.g, names, tags, etc)
        import mysubmodule
        tt.include(mysubmodule, filter=lambda t: t.important)
    ```

    Passing a already existing Task object is less common, but possible.
    Doing so will simply copy that task it to the calling module.

    For more on including tasks see, see docs.
    """
    if to_module is None:
        to_module = utils.get_callers_module()

    from .tt import Task

    if "filter" in kwargs and not isinstance(object, Module):
        msg = "include(): 'filter' parameter is only supported when including entire modules"
        raise Exception(msg)

    if isinstance(object, Module):
        return include_module(
            object, to_module=to_module, namespace=namespace, alias_namespace=alias_namespace, **kwargs
        )
    elif inspect.isfunction(object):
        return [
            include_function(
                object, to_module=to_module, namespace=namespace, alias_namespace=alias_namespace, **kwargs
            )
        ]
    elif isinstance(object, Task):
        from_module: Module = sys.modules[object.func.__module__]
        from .include import _include_task

        return [
            _include_task(
                object,
                from_module=from_module,
                to_module=to_module,
                namespace=namespace,
                alias_namespace=alias_namespace,
                **kwargs,
            )
        ]
    else:
        msg = f"include(): Unsupported type: {type(object)}"
        raise Exception(msg)


def include_module(
    from_module: Module,
    *,
    to_module: Module | None = None,
    skip_include_info: bool = False,
    namespace: str = "",
    alias_namespace: str = "",
    filter: Callable[[Task], bool] = lambda t: not t.hidden,
) -> list[Task]:
    """Include all tasks from the specified python module.

    When including the main module, we skip the include info, as then all the
    tasks would be marked as included.
    """
    if to_module is None:
        to_module = utils.get_callers_module()

    if not hasattr(from_module, "decorated_functions"):
        from_module.decorated_functions = []  # type: ignore[attr-defined]

    if not hasattr(to_module, "decorated_functions"):
        to_module.decorated_functions = []  # type: ignore[attr-defined]

    # make a copy, as we will the original list in _include_task if from_module==to_module,
    tasks = from_module.decorated_functions[:]
    out: list[Task] = []
    for task in tasks:
        if not skip_include_info:  # otherwise we will filter out the ones included from root module
            if not filter(task):
                continue
        # copy the task to the current module
        out.append(
            _include_task(
                task=task,
                from_module=from_module,
                to_module=to_module,
                skip_include_info=skip_include_info,
                namespace=namespace,
                alias_namespace=alias_namespace,
            )
        )
    return out


def include_function(
    function: AnyFunction,
    *,
    to_module: Module | None = None,
    skip_include_info: bool = False,
    namespace: str = "",
    alias_namespace: str = "",
    **kwargs: Any,
) -> Task:
    """Include a function as a task. The function must have been decorated with @task.

    Typically you include a imported function from another module.
    You can laso include tasks from the same module to e.g. copy them to a different group.

    Example:
    ```
        from module import mytask
        tt.include_function(mytask)
    ```

    Example:
    ```
        # This will prefix included function with a namespace
        from module import mytask
        with tt.group("othergroup", namespace="group"):
            tt.include_function(mytask)
    ```
    """
    if to_module is None:
        to_module = utils.get_callers_module()

    fun = function
    module_of_fun = sys.modules[fun.__module__]
    task: None | Task = None
    for atask in module_of_fun.decorated_functions:
        if atask.func == fun:
            task = atask
            break
    if not task:
        # function has not been decorated with @task yet, decore it, so that we can include it

        msg = "included function was not decorated with @task"
        raise Exception(msg)

    return _include_task(
        task=task,
        from_module=module_of_fun,
        to_module=to_module,
        skip_include_info=skip_include_info,
        namespace=namespace,
        alias_namespace=alias_namespace,
        **kwargs,
    )


def _include_task(
    task: Task,
    from_module: Module,
    to_module: Module,
    skip_include_info: bool = False,
    namespace: str = "",
    alias_namespace: str = "",
) -> Task:
    """Shared code for including a task from one module to another."""
    if not hasattr(from_module, "decorated_functions"):
        from_module.decorated_functions = []  # type: ignore[attr-defined]

    if not hasattr(to_module, "decorated_functions"):
        to_module.decorated_functions = []  # type: ignore[attr-defined]

    assert isinstance(task, Task), f"Expected Task, got {type(task)}"

    if not skip_include_info:
        group = get_current_group()
        copy = task.copy(group=group, included_from=from_module)
        copy.add_namespace_from_group(task.group)
        copy.included_from = from_module  # ensure is set
    else:
        # We're including the root module, preserve the group info, otherwise we would move all tasks to 'default'
        copy = task  # dont copy at all, just ues the group
        # group = task.group
        # copy = task.copy(group=group, included_from=None)

        # # So that those which were included into the root module continue to be marked as included
        # if task.included_from:
        #     copy.included_from = task.included_from

    if namespace:
        copy.add_namespace(namespace, alias_namespace=alias_namespace)

    existing_tasks = [t for t in to_module.decorated_functions if t.name == copy.name]
    if existing_tasks:
        msg = f"Task '{copy.name}' included from {from_module.__file__} already exists in module {to_module.__file__}."
        raise UserError(msg)

    to_module.decorated_functions.append(copy)
    log.debug(f"include_module(): including task {task.name} from {from_module.__file__} to {to_module.__file__}")
    return copy


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
