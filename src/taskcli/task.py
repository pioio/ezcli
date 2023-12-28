import functools
import inspect
import os
import sys
from dataclasses import dataclass
from typing import Callable, Iterable

import taskcli.core

from . import utils
from .configuration import config
from .group import DEFAULT_GROUP, Group
from .parameter import Parameter
from .tags import TAG_IMPORTANT
from .types import Any, AnyFunction


class UserError(Exception):
    """Print nice error to the user."""


@dataclass
class TaskCodeLocation:
    """Where the task is defined."""

    file: str
    line: int

    def __str__(self) -> str:
        return f"{self.file}:{self.line}"

    def __repr__(self) -> str:
        return f"TaskCodeLocation(file={self.file!r}, line={self.line!r})"


def task(*args: Any, **kwargs: Any) -> AnyFunction:
    """Decorate a function as a task."""
    # currentframe is much(!) faster than inspect.stack()

    kwargs["code_location"] = _get_code_location()

    if len(args) == 1 and callable(args[0]):
        # Decorator is used without arguments
        return _get_wrapper(args[0], **kwargs)
    else:
        # Decorator is used with arguments

        # Which functool wrap to add???
        def decorator(func: AnyFunction) -> AnyFunction:
            return _get_wrapper(func, *args, **kwargs)

        return decorator


def _get_code_location() -> TaskCodeLocation:
    """Inspects the stack to find the location of the task definition.

    This info is later used to print warnings about the task.
    This function can be called only from the @task decorator.
    """
    current_frame = inspect.currentframe()
    assert current_frame is not None

    prev_fame = current_frame.f_back
    assert prev_fame is not None

    prev_fame = current_frame.f_back
    assert prev_fame is not None

    file_location = prev_fame.f_code.co_filename
    line_number = prev_fame.f_lineno

    return TaskCodeLocation(file=file_location, line=line_number)


class Task:
    """A decorated function."""

    def copy(self, group: Group) -> "Task":
        """Return a copy of the task."""
        new_task = Task(
            func=self.func,
            group=group,
        )
        for prop in self.__dict__:
            # TODO explicit copy of some objects, code_location
            props_to_skip = [
                "func",  # passed to constructor
                "params",
                "group",  # created from func in constructor  # passed to constructor
            ]
            if prop in props_to_skip:
                continue

            # For everything else shallow copy should be good enough here
            setattr(new_task, prop, getattr(self, prop))
        return new_task

    def __init__(
        self,
        func: AnyFunction,
        custom_name: str = "",
        custom_desc: str = "",
        group: Group | None = None,
        hidden: bool = False,
        aliases: Iterable[str] | None = None,
        important: bool = False,
        env: list[str] | None = None,
        format: str = "{name}",
        customize_parser: Callable[[Any], None] | None = None,
        is_go_task: bool = False,
        suppress_warnings: bool = False,
        code_location: TaskCodeLocation | None = None,
        tags: list[str] | None = None,
    ):
        """Create a new Task.

        func: The decorated python function.
        hidden: If True, the task will not be listed in the help by default.
        important: If True, the task will be listed in the help in a way which stands out. See config for details.
        """
        self.custom_name = custom_name  # entirely optional
        self.custom_desc = custom_desc  # entirely optional
        self.func = func
        self.aliases = aliases or []
        self.tags = tags or []
        self.env = env or []
        self.hidden = hidden
        self.important = important
        if important and TAG_IMPORTANT not in self.tags:
            self.tags.append(TAG_IMPORTANT)

        self.params = [Parameter(param) for param in inspect.signature(func).parameters.values()]
        self.name_format = format
        self.customize_parser = customize_parser
        self.is_go_task: bool = is_go_task
        self.suppress_warnings: bool = suppress_warnings

        self.group: Group = group or DEFAULT_GROUP

        if self not in self.group.tasks:
            self.group.tasks.append(self)

        self.code_location = code_location or TaskCodeLocation(file="<unknown>", line=0)

        self.soft_validate_task()

    def is_valid(self) -> bool:
        """Return True if the task is valid."""
        num_fatal_errors = len([err for err in get_validation_errors(self) if err.fatal])
        return num_fatal_errors == 0

    def soft_validate_task(self) -> None:
        """Print a warning if the task is not valid, but don't fail. a Pre-validation.

        The idea here is that we don't want to prevent listing tasks due to issues with only one tasks.
        That would be annoying. Instead, we want to print a warning, and then fail only
        if the user tries to actually run the affected task.
        """
        if self.suppress_warnings:
            return
        errors = get_validation_errors(self)
        for error in errors:
            text = error.msg
            if error.fatal:
                text += " Attempting to run this task fill fail."
            utils.print_warning(text)

    def is_hidden(self) -> bool:
        """Return True if the task is hidden."""
        return self.hidden or self.func.__name__.startswith("_")

    @property
    def name(self) -> str:
        """Return the name of the task."""
        return self.get_full_task_name()

    def get_full_task_name(self) -> str:
        """Return the full name of the task, including the group."""
        if self.custom_name:
            return self.custom_name
        out = self.func.__name__.replace("_", "-")
        out.lstrip("-")  # for _private functions

        return out

    def get_all_task_names(self) -> list[str]:
        """Return all names of the task, including aliases."""
        return [self.get_full_task_name(), *self.aliases]

    def get_summary_line(self) -> str:
        """Return the first line of docstring, or empty string if no docstring."""
        if self.custom_desc:
            return self.custom_desc.split("\n")[0]
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

    def dispatch(self, args: list[str] | str | None = None, sysexit_on_user_error: bool = True) -> Any:
        """Dispatch the task. A helper for unit tests."""
        name = self.get_full_task_name()
        from .parser import dispatch

        if isinstance(args, str):
            args = [args]

        if args:
            res = dispatch([name, *args], sysexit_on_user_error=sysexit_on_user_error)
        else:
            res = dispatch([name], sysexit_on_user_error=sysexit_on_user_error)
        return res


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
        runtime = taskcli.core.get_runtime()
        runtime.tasks.append(task)

    return wrapper_for_changing_directory


@dataclass
class ValidationResult:
    """A validation result of a task."""

    msg: str = ""
    fatal: bool = False


def get_validation_errors(task: Task) -> list[ValidationResult]:
    """Return a list of validation errors for the task.

    Error can be fatal (task can't be run), or not.
    """
    # validate params
    out: list[ValidationResult] = []
    suppress_hint = "Add `suppress_warnings=True` to the task decorator to suppress this warning."

    for param in task.params:
        if param.type.is_bool() and param.kind not in [Parameter.KEYWORD_ONLY]:
            # This will be a common error, so make sure the error message is extra helpful
            msg = (
                f"Task '{task.name}' ({task.code_location}) has a "
                f"boolean parameter '{param.name}' which is not keyword-only. "
                "This is not supported. "
                f"Either make the boolean parameter explicitly a keyword-only parameter by "
                "adding `*,` in the param list "
                "anywhere before the bool parameter "
                f"[e.g. def taskname(arg:name, *, {_helper_render_bool_example(param)}) ], or use a different type."
            )
            out += [ValidationResult(msg, fatal=True)]
        if not param.type.has_supported_type():
            msg = f"Task '{task.name}' has a parameter '{param.name}' which has an unsupported type {param.type.raw}. "
            if param.has_default():
                msg += (
                    "It will not be possible to specify this parameter from the CLI. "
                    "When invoking the task the param default value will be used."
                )
                msg += " " + suppress_hint
                fatal = False
            else:
                msg += "The parameter does not have a default value set, so taskcli cannot skip adding it to argparse."
                msg += "Either add a default value to this parameter, or change the type to a supported type."
                fatal = True
            out += [ValidationResult(msg, fatal=fatal)]

    return out


def _helper_render_bool_example(param: Parameter) -> str:
    """Render a bool parameter to string for an the warning text."""
    out = param.name
    if param.type.was_specified():
        out += ":bool"
    if param.has_default():
        out += f"={param.default}"
    return out
