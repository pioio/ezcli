import functools
import inspect
import os
import sys
from typing import Callable, Iterable

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

    def copy(self, group: Group) -> "Task":
        """Return a copy of the task."""
        new_task = Task(
            func=self.func,
            group=group,
        )
        for prop in self.__dict__:
            props_to_skip = [
                "func",  # passed to constructor
                "params" "group",  # created from func in constructor  # passed to constructor
            ]
            if prop in props_to_skip:
                continue

            # For everything else shallow copy should be good enough here
            setattr(new_task, prop, getattr(self, prop))
        return new_task

    def __init__(
        self,
        func: AnyFunction,
        group: Group | None = None,
        hidden: bool = False,
        aliases: Iterable[str] | None = None,
        important: bool = False,
        env: list[str] | None = None,
        format: str = "{name}",
        customize_parser: Callable[[Any], None] | None = None,
    ):
        """Create a new Task.

        func: The decorated python function.
        hidden: If True, the task will not be listed in the help by default.
        important: If True, the task will be listed in the help in a way which stands out. See config for details.
        """
        self.func = func
        self.aliases = aliases or []
        self.env = env or []
        self.hidden = hidden
        self.important = important
        self.params = [Parameter(param) for param in inspect.signature(func).parameters.values()]
        self.name_format = format
        self.customize_parser = customize_parser

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

        filepath = inspect.getfile(module)  # type: ignore[arg-type]
        dirpath = os.path.dirname(filepath)
        return dirpath

    def is_ready(self) -> bool:
        """Return the directory in which the task was define."""
        import os

        if not self.env_is_ready():
            return False
        return True

    def get_not_ready_reason_short(self) -> str:
        """Get a short string explaining why the task is not ready to run."""
        reasons = []
        if not self.env_is_ready():
            reasons.append("env!")
        # TODO: add custom function
        # > if not self.fun_is_ready():
        # >     reasons.append("check!")
        return ", ".join(reasons)

    def get_not_ready_reason_long(self) -> list[str]:
        """Get a detailed list of reasons why the task is not ready to run."""
        reasons = []
        for env in self.env:
            if env not in os.environ:
                reasons.append(f"Env var {env} is not set.")
            elif os.environ[env] == "":
                reasons.append(f"Env var {env} is set but is empty.")
        return reasons

    def env_is_ready(self) -> bool:
        """Return true if the env variables required by the task are set."""
        for env in self.env:
            if env not in os.environ or os.environ[env] == "":
                return False
        return True

    def get_missing_env(self) -> list[str]:
        """Return the directory in which the task was define."""
        import os

        missing = []
        for env in self.env:
            if env not in os.environ or os.environ[env] == "":
                missing.append(env)
        return missing


def _get_wrapper(  # noqa: C901
    func: AnyFunction,
    group: Group | None = None,
    hidden: bool = False,
    prefix: str = "",
    important: bool = False,
    aliases: Iterable[str] | None = None,
    change_dir: bool = True,
    env: list[str] | None = None,
    **other_kwargs: Any,
) -> AnyFunction:
    # TODo: allow defining groups via string at task-creationg time
    # >  if isinstance(group, str):
    # >      if group == "default":
    # >          group = DEFAULT_GROUP
    # >      else:
    # >          group = Group(name=group)
    aliases = aliases or []
    env = env or []

    if config.adv_auto_hide_private_tasks and (func.__name__.startswith("_") and not hidden):
        func.__name__ = func.__name__.lstrip("_")
        hidden = True
    if prefix:
        func.__name__ = prefix + "_" + func.__name__

    kwargs = locals() | other_kwargs
    del kwargs["other_kwargs"]
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
    def wrapper_for_changing_directory(*args: list[Any], **kwargs: dict[str, Any]) -> Any:
        if change_dir:
            with utils.change_dir(task.get_taskfile_dir()):  # type: ignore[attr-defined]
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    del kwargs["group"]
    del kwargs["aliases"]
    del kwargs["env"]
    task = Task(wrapper_for_changing_directory, env=env, group=group, aliases=aliases, **kwargs)

    if not hasattr(module_which_defines_task, "decorated_functions"):
        module_which_defines_task.decorated_functions = []  # type: ignore[attr-defined]

    # Ensure no double decoration
    for atask in module_which_defines_task.decorated_functions:
        if atask.func == func:
            msg = f"Function {func} is already decorated as a task"
            raise ValueError(msg)

    module_which_defines_task.decorated_functions.append(task)

    if module_which_defines_task_name == "__main__":
        # Auto-include to the runtime if the module defining the tasks is the one we started (./tasks.py)
        # everything else needs to be explicitly included
        runtime = utils.get_runtime()
        runtime.tasks.append(task)

    return wrapper_for_changing_directory
