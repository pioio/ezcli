import functools
import inspect
import sys
from typing import Iterable

from . import utils
from .configuration import config
from .group import DEFAULT_GROUP, Group
from .parameter import Parameter
from .types import Any, AnyFunction


def task(*args: Any, **kwargs: Any) -> AnyFunction:
    """Decorate a function as a task."""
    if len(args) == 1 and callable(args[0]):
        # Decorator is used without arguments
        return _get_wrapper(args[0])
    else:
        # Decorator is used with arguments

        # Which functool wrap to add???
        def decorator(func: AnyFunction) -> AnyFunction:
            return _get_wrapper(func, *args, **kwargs)

        return decorator


class Task:
    """A decorated function."""

    def __init__(
        self,
        func: AnyFunction,
        group: Group | None = None,
        hidden: bool = False,
        aliases: Iterable[str] | None = None,
        important: bool = False,
    ):
        """Create a new Task.

        func: The decorated python function.
        hidden: If True, the task will not be listed in the help by default.
        important: If True, the task will be listed in the help in a way which stands out. See config for details.
        """
        self.func = func
        self.aliases = aliases or []
        self.hidden = hidden
        self.important = important
        self.params = [Parameter(param) for param in inspect.signature(func).parameters.values()]

        self.group: Group = group or DEFAULT_GROUP

        if self not in self.group.tasks:
            self.group.tasks.append(self)

    def is_hidden(self) -> bool:
        """Return True if the task is hidden."""
        return self.hidden or self.func.__name__.startswith("_")

    @property
    def name(self) -> str:
        """Return the name of the task."""
        return self.get_full_task_name()

    def get_full_task_name(self) -> str:
        """Return the full name of the task, including the group."""
        out = self.func.__name__.replace("_", "-")
        out.lstrip("-")  # for _private functions

        if self.hidden:
            out = "_" + out
        return out

    def get_all_task_names(self) -> list[str]:
        """Return all names of the task, including aliases."""
        return [self.get_full_task_name(), *self.aliases]

    def get_summary_line(self) -> str:
        """Return the first line of docstring, or empty string if no docstring."""
        if self.func.__doc__ is None:
            return ""
        return self.func.__doc__.split("\n")[0]

    def get_taskfile_dir(self) -> str:
        """Return the directory in which the task was define."""
        func = self.func
        # get directory in which this file is located
        import inspect
        import os

        module = inspect.getmodule(func)

        filepath = inspect.getfile(module)
        dirpath = os.path.dirname(filepath)
        return dirpath


def _get_wrapper(
    func: AnyFunction,
    group: Group | None = None,
    hidden: bool = False,
    prefix: str = "",
    important: bool = False,
    aliases: Iterable[str] | None = None,
    change_dir: bool = True,
) -> AnyFunction:
    # TODo: allow defining groups via string at task-creationg time
    # >  if isinstance(group, str):
    # >      if group == "default":
    # >          group = DEFAULT_GROUP
    # >      else:
    # >          group = Group(name=group)
    aliases = aliases or []

    if config.adv_auto_hide_private_tasks and (func.__name__.startswith("_") and not hidden):
        func.__name__ = func.__name__.lstrip("_")
        hidden = True
    if prefix:
        func.__name__ = prefix + "_" + func.__name__

    kwargs = locals()
    del kwargs["func"]
    del kwargs["prefix"]
    del kwargs["change_dir"]

    import os

    module_which_defines_task_name = func.__module__
    module_which_defines_task = sys.modules[module_which_defines_task_name]

    from .group import get_current_group

    if group is None:
        group = get_current_group()
    assert isinstance(group, Group), f"Expected group to be a Group, got {group!r}"

    if isinstance(aliases, str):
        aliases = [aliases]


    # DecoratedFunction
    @functools.wraps(func)
    def wrapper(*args: list[Any], **kwargs: dict[str, Any]) -> Any:

        if change_dir:
            with utils.change_dir(task.get_taskfile_dir()):
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)



    del kwargs["group"]
    del kwargs["aliases"]
    task = Task(wrapper, group=group, aliases=aliases, **kwargs)

    if not hasattr(module_which_defines_task, "decorated_functions"):
        module_which_defines_task.decorated_functions = []  # type: ignore[attr-defined]

    module_which_defines_task.decorated_functions.append(task)

    if module_which_defines_task_name == "__main__":
        # Auto-include to the runtime if the module defining the tasks is the one we started (./tasks.py)
        # everything else needs to be explicitly included
        runtime = utils.get_runtime()
        runtime.tasks.append(task)


        #return func(*args, **kwargs)

    # # change dir
    # if change_dir:
    #     pare
    #     @functools.wraps(wrapper)
    #     def wrapper2(*args: list[Any], **kwargs: dict[str, Any]) -> Any:
    #         with utils.change_dir():
    #             return func(*args, **kwargs)

    return wrapper
