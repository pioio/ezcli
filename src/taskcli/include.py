"""Logic for including Tasks from other modules."""

from dataclasses import dataclass
import importlib.util
import inspect
import logging
import os
import sys
from contextlib import contextmanager
from posixpath import isabs
from typing import Callable
from unicodedata import name

from genericpath import isdir

import taskcli

from . import core, utils
from .group import get_current_group
from .logging import get_logger
from .task import Task
from .types import Any, AnyFunction, Module, UserError

log = get_logger(__name__)

# Global list of all included modules, used to prevent circular includes
_included_module_paths = []

from .modulesettings import get_module_settings



def include_parent(filter:Callable[["Task"], Any]|None=None) -> None:
    """Find a parent tasks.py and include it.

    Runs only one time, once the main taskfile (and its includes) has been imported and included.
    """
    module = utils.get_callers_module()
    settings = get_module_settings(module)
    settings.include_parent = True
    settings.parent_task_filter = filter


def include(
    object: Module | AnyFunction | "Task" | str,
    /,
    *,
    to_module: Module | None = None,
    name_namespace: str = "",
    alias_namespace: str = "",
    name_namespace_if_conflict: str = "",
    **kwargs: Any,
) -> list["Task"]:
    """Include Tasks from the specified object into the module which is calling this function. Returns included Tasks.

    WHen including a module, functions already present will be automatically skipped
    When including a function or Task, if the task of that name exists, an error will be raised.

    This function is meant to be called directly from a ./tasks.py file.
    This function is a convenience wrapper around `include_module()` and `include_function()`.

    For more control, call the lower level `include_module()` or `include_function()` directly.

    NOTE: if "object" is a relative path, that path will be interpreted as
          relative to the module to which we're including. Not as relative to the current working dir.
          This resembles how python imports work, and is required to make "t -f foo/tasks.py" to
          properly include "foo/subsubdir/tasks.py" when the "foo/tasks.py" calls "tt.include("subsubdir/tasks.py").


    Example:
    ```
        # Most basic usage import and then include a module from a path
        tt.include("../../path/to/tasks.py")

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
    log.debug(f"include(): start: {object=} {to_module=} {id(to_module)=}")

    from .tt import Task

    if "filter" in kwargs and (not isinstance(object, Module) and not isinstance(object, str)):
        msg = "include(): 'filter' parameter is only supported when including entire modules"
        raise Exception(msg)

    #log.info("FILTER:" + str(kwargs.get("filter", None)))

    tasks: list[Task] = []
    if isinstance(object, Module):
        tasks = include_module(
            object, to_module=to_module, name_namespace=name_namespace, alias_namespace=alias_namespace, **kwargs
        )
    elif inspect.isfunction(object):
        tasks = [
            include_function(
                object, to_module=to_module, namespace=name_namespace, alias_namespace=alias_namespace, **kwargs
            )
        ]
    elif isinstance(object, str):
        # Turne relative include path into an absolute path RELATIVE to the module to which we're including
        # otherwise doing relative imports after `task -f somedir/tasks.py` will not work as the imports will
        # be relative to the current working directory, not the tasks.py file.
        path = object
        if os.path.isabs(path):
            log.trace(f"include(str): Path {path=} is already absolute, not changing it.")
            # already is abs
        else:
            to_module_file = to_module.__file__
            assert to_module_file is not None
            to_module_dirpath = os.path.dirname(to_module_file)
            new_path = os.path.abspath(os.path.join(to_module_dirpath, path))
            log.trace(
                f"include(str): Turned relative import path {path} (relative to "
                f"the module) into an absolute path:l {new_path}"
            )
            path = new_path

        if not os.path.isfile(path):
            # TODO unit test
            msg = f"include(): provided path {path=} is not a regular file"
            raise UserError(msg)
        if not path.endswith(".py"):
            # TODO unit test
            msg = f"include(): provided path {path=} does not end with .py"
            raise UserError(msg)

        from_module = import_module_from_path(path, path)
        log.debug(
            f"include(str): now including tasks from imported module to module {to_module.__name__} {id(to_module)=}."
        )
        tasks = include_module(
            from_module, to_module=to_module, name_namespace=name_namespace,name_namespace_if_conflict=name_namespace_if_conflict, alias_namespace=alias_namespace, **kwargs
        )

    elif isinstance(object, Task):
        from_module: Module = sys.modules[object.func.__module__]
        from .include import _include_task

        tasks = [
            _include_task(
                object,
                from_module=from_module,
                to_module=to_module,
                name_namespace=name_namespace,
                alias_namespace=alias_namespace,
                **kwargs,
            )
        ]
    else:
        msg = f"include(): Unsupported type: {type(object)}"
        raise Exception(msg)

    log.debug(
        f"include() end: included {len(tasks)} tasks from {object} to module {to_module.__name__} ({id(to_module)=})"
    )
    for task in tasks:
        log.debug(f"  include() end: {task.name=}")
    return tasks


def include_module(
    from_module: Module,
    *,
    to_module: Module | None = None,
    skip_include_info: bool = False,
    name_namespace: str = "",
    alias_namespace: str = "",
    name_namespace_if_conflict: str = "",
    filter: Callable[[Task], bool] | None = None,
) -> list[Task]:
    """Include all tasks from the specified python module.

    When including the main module, we skip the include info, as then all the
    tasks would be marked as included.
    """
    if filter is None and not skip_include_info:
        log.debug("No filter set, including all not hidden tasks")

        def filter_not_hidden(t: Task) -> bool:
            return not t.hidden

        filter = filter_not_hidden
    else:
        log.debug("Using custom filter")

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
        # if not skip_include_info:  # otherwise we will filter out the ones included from root module
        #if filter:
        if filter and not filter(task):
            continue

        # copy the task to the current module
        try:
            added_task = _include_task(
                task=task,
                from_module=from_module,
                to_module=to_module,
                skip_include_info=skip_include_info,
                name_namespace=name_namespace,
                alias_namespace=alias_namespace,
            )
        except TaskExistsError as _:
            if not name_namespace_if_conflict:
                log.debug(
                    f"include_module: Task {task.name} already exists "
                    f" in module {to_module.__name__} {id(to_module)=}, no {name_namespace_if_conflict=} set, skipping"
                )
                utils.print_warning(f"Task {task.name} already exists, not including it")
                continue
            else:
                try:
                    added_task = _include_task(
                        task=task,
                        from_module=from_module,
                        to_module=to_module,
                        skip_include_info=skip_include_info,
                        name_namespace=name_namespace_if_conflict + name_namespace,
                        alias_namespace=alias_namespace,
                    )
                except TaskExistsError as _:
                    log.debug(
                        f"include_module: Task {task.name} already exists, skipping "
                    )
                    utils.print_warning(f"Task {task.name} already exists, not including it")
                    continue

        out.append(added_task)
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
        name_namespace=namespace,
        alias_namespace=alias_namespace,
        **kwargs,
    )


class TaskExistsError(Exception):
    """Raised iff a task already exists in a module and thus cannot be added to it."""


def _include_task(
    task: Task,
    from_module: Module,
    to_module: Module,
    skip_include_info: bool = False,
    name_namespace: str = "",
    alias_namespace: str = "",
) -> Task:
    """Shared code for including a task from one module to another."""
    if not hasattr(from_module, "decorated_functions"):
        from_module.decorated_functions = []  # type: ignore[attr-defined]

    if not hasattr(to_module, "decorated_functions"):
        to_module.decorated_functions = []  # type: ignore[attr-defined]

    assert isinstance(task, Task), f"Expected Task, got {type(task)}"

    if not skip_include_info:
        target_group = get_current_group(to_module)
        copy = task.copy(group=target_group, included_from=from_module)
        copy.add_namespace_from_group(task.group)
        copy.included_from = from_module  # ensure is set
        copy.distance = task.distance + 1
    else:
        # We're including the root module, preserve the group info, otherwise we would move all tasks to 'default'
        copy = task  # dont copy at all
        # but at

    if name_namespace:
        copy.add_namespace(name_namespace, alias_namespace=alias_namespace)

    existing_tasks = [t for t in to_module.decorated_functions if t.name == copy.name]
    if existing_tasks:
        msg = (
            f"Task '{copy.name}' included from {from_module.__file__} already exists in "
            f"module {to_module.__file__}. Cannot include it again under the same. Consider using a namespace."
        )
        raise TaskExistsError(msg)

    to_module.decorated_functions.append(copy)

    log.trace(f"include_module(): including task {task.name} from {from_module.__file__} to {to_module.__file__}")
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
        log.debug(f"load_tasks_from_module_to_runtime(): including task {task.name} from {module.__name__}  to runtime")
        runtime.tasks.append(task)


@contextmanager
def _add_to_sys_path(path):
    old_sys_path = sys.path.copy()
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path = old_sys_path


class TaskImportError(Exception):
    """Raised when a task cannot be imported."""


def task_already_present(task: Task, module: Module) -> bool:
    """Check if a task is already present in a module."""
    if not hasattr(module, "decorated_functions"):
        module.decorated_functions = []  # type: ignore[attr-defined]

    for t in module.decorated_functions:
        if t.name == task.name:
            return True
    return False


# Define a function to import a module from a given path
def import_module_from_path(module_name, path) -> Module:
    """Import a module from a given path."""
    prefix = "import_module_from_path(): "
    abspath = os.path.abspath(path)
    assert os.path.isabs(path)
    log.trace(f"{prefix}: start: {module_name=} {path=}")
    path = abspath

    if os.path.isdir(path):
        log.trace(f"{prefix}: path is a dir: {path}, looking for taskspy")
        valid_taskspy = _find_valid_taskspy_in_dir(path)
        to_import = valid_taskspy
        if not valid_taskspy:
            msg = f"{prefix}: Could not find a valid tasks.py file in {path}"
            raise TaskImportError(msg)
        else:
            log.debug(f"{prefix}: Found valid tasks.py file: {valid_taskspy}")
            path = os.path.join(path, valid_taskspy)

    else:
        log.trace(f"{prefix}: path is a file: {path}")
        to_import = path

    module_dir = os.path.dirname(path)

    log.trace(f"{prefix}, proceeding with import")

    if abspath in sys.modules:
        log.debug(f"{prefix}: module {abspath} already imported, skipping")
        return sys.modules[abspath]

    with _add_to_sys_path(module_dir):
        spec = importlib.util.spec_from_file_location(abspath, to_import)
        module = importlib.util.module_from_spec(spec)
        sys.modules[abspath] = module
        from .timer import Timer
        with Timer(f"Loading module {abspath}"):
            spec.loader.exec_module(module)
    log.debug(f"{prefix}: import of {path} complete")
    return module


def _get_valid_taskspy_filenames() -> list[str]:
    """Return a list of valid filenames for the tasks.py file."""
    from . import envvars

    out = envvars.TASKCLI_TASKS_PY_FILENAMES.value.split(",")
    return out


def _find_valid_taskspy_in_dir(dirpath) -> str:
    valid_filenames = _get_valid_taskspy_filenames()
    for filename in os.listdir(dirpath):
        if filename in valid_filenames and os.path.isfile(filename):
            return os.path.join(dirpath, filename)
    return ""
