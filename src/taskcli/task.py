import functools
import sys

from .configuration import config
from .decoratedfunction import Task
from .group import Group
from .types import Any, AnyFunction



def task(*args:Any, **kwargs:Any) -> AnyFunction:
    if len(args) == 1 and callable(args[0]):
        # Decorator is used without arguments
        return _get_wrapper(args[0])
    else:
        # Decorator is used with arguments
        def decorator(func:AnyFunction) -> AnyFunction:
            return _get_wrapper(func, *args, **kwargs)

        return decorator

from . import utils

def _get_wrapper(func:AnyFunction, group: str | Group = "default", hidden: bool = False, prefix: str = "", important: bool = False) -> AnyFunction:
    if isinstance(group, str):
        group = Group(name=group)
    if config.adv_hide_private_tasks and (func.__name__.startswith("_") and not hidden):
        # func.__name__ = func.__name__[1:]
        # lstrip _
        func.__name__ = func.__name__.lstrip("_")
        hidden = True
    if prefix:
        func.__name__ = prefix + "_" + func.__name__

    kwargs = locals()
    del kwargs["func"]
    del kwargs["prefix"]

    module_which_defines_task_name = func.__module__
    module_which_defines_task = sys.modules[module_which_defines_task_name]


    decorated = Task(func, **kwargs)
    if not hasattr(module_which_defines_task, "decorated_functions"):
        module_which_defines_task.decorated_functions:list[Task] = []  # type: ignore

    module_which_defines_task.decorated_functions.append(decorated)

    if module_which_defines_task_name == "__main__":
        # Auto-include to the runtime if the module defining the tasks is the one we started (./tasks.py)
        # everything else needs to be explicitly included
        runtime = utils.get_runtime()
        runtime.tasks.append(decorated)

    # DecoratedFunction
    @functools.wraps(func)
    def wrapper(*args:list[Any], **kwargs:dict[str,Any]) -> Any:
        return func(*args, **kwargs)

    return wrapper


