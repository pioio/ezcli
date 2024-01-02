import functools
import inspect
import os
import sys
from ast import Mod
from dataclasses import dataclass
from hmac import new
from typing import Callable, Iterable

import taskcli.core
from taskcli import configuration

from . import utils
from .configuration import config
from .constants import NAMESPACE_SEPARATOR
from .group import Group
from .parameter import Parameter
from .tags import TAG_IMPORTANT
from .types import Any, AnyFunction, Module


@dataclass
class TaskCodeLocation:
    """Where the task is defined."""

    file: str
    line: int

    def __str__(self) -> str:
        return f"{self.file}:{self.line}"

    def __repr__(self) -> str:
        return f"TaskCodeLocation(file={self.file!r}, line={self.line!r})"


def task_decorator(
    *args: Any,
    change_dir: bool = True,
    # ------------ args below are copy-pasted from the Task.__init__
    # We don't specify those via **kwargs to get a better IDE experience
    name: str = "",
    desc: str = "",
    group: Group | None = None,
    hidden: bool = False,
    aliases: Iterable[str] | str | None = None,
    important: bool = False,
    env: list[str] | None = None,
    format: str = "{name}",
    customize_parser: Callable[[Any], None] | None = None,
    suppress_warnings: bool = False,
    tags: list[str] | None = None,
    is_go_task: bool = False,
) -> AnyFunction:
    """Create a new Task. This is a decorator, use it on function to create new tasks.

    Args:
        change_dir: whether to change directory to the directory where this task is defined.
        name: optional name of the task. By default it's the name of the function.
        desc: optional description of the task. By default it's the first line of the docstring.
        group: optional group of the task. By default it's the current group or the default group
        important: If True, the task will be listed in a way which stands out
        hidden: If True, the task will not be listed by default in `taskcli` output (use `tt` to list).
        aliases: Optional list of aliases for the task. Can be a string, or iterable
        env: Optional list of environment variables which must be set for the task to be runnable.
        format: Optional format string for the name of the task. You can use colors like e.g. "{red}{name}{clear}".
        customize_parser: Optional function which can customize the argparse parser for the task.
        suppress_warnings: If True, warnings about the task being misconfigure will not be printed.
        tags: Optional list of tags for the task. Tags are used to filter tasks with `-t <tag>`
        args: optional arguments to the task decorator. Ignore those.
        is_go_task: used internally to mark tasks imported from the go-task project.


    """
    # currentframe is much(!) faster than inspect.stack()
    kwargs = locals()
    del kwargs["args"]

    if len(args) == 1 and callable(args[0]):
        # Decorator is used without arguments
        return _get_wrapper(args[0], **kwargs)
    else:
        # Decorator is used with arguments

        # Which functool wrap to add???
        def decorator(func: AnyFunction) -> AnyFunction:
            return _get_wrapper(func, *args, **kwargs)

        return decorator


class Task:
    """Represents a single task. Gets created via the `@task` decorator."""

    def __init__(
        self,
        # Args below can be copy-pasted to the `def task` decorator
        func: AnyFunction,
        group: Group,
        name: str = "",
        desc: str = "",
        hidden: bool = False,
        aliases: Iterable[str] | str | None = None,
        important: bool = False,
        env: list[str] | None = None,
        format: str = "{name}",
        customize_parser: Callable[[Any], None] | None = None,
        suppress_warnings: bool = False,
        tags: list[str] | None = None,
        is_go_task: bool = False,
        # ------------ don't include those in 'def task'
        code_location: TaskCodeLocation | None = None,
        included_from: Module | None = None,
    ):
        """Create a new Task.

        func: The decorated python function.
        hidden: If True, the task will not be listed in the help by default.
        important: If True, the task will be listed in the help in a way which stands out. See config for details.
        """

        self._name = name  # entirely optional
        self._desc = desc  # entirely optional
        self.func = func
        self.name_namespaces: list[str] = []
        self._extra_summary: list[str] = []
        if isinstance(aliases, str):
            aliases = [aliases]
        self._aliases = aliases or []

        self.tags = tags or []
        self.env = env or []
        self.hidden = hidden
        self.important = important
        self.from_above = False
        self.from_parent = False
        if important and TAG_IMPORTANT and TAG_IMPORTANT not in self.tags:
            self.tags.append(TAG_IMPORTANT)

        from taskcli import tt

        if tt.config.hide_not_ready and not self.is_ready():
            self.hidden = True
            self._extra_summary += ["(auto hidden)"]

        self.params = [Parameter(param) for param in inspect.signature(func).parameters.values()]
        self.name_format = format
        self.customize_parser = customize_parser
        self.is_go_task: bool = is_go_task
        self.suppress_warnings: bool = suppress_warnings
        self.distance: int = 0  # Distance (number of includes) away from the root tasks.py file. 0==root tasks.py

        assert group
        self.group: Group = group

        if self not in self.group.tasks:
            self.group.tasks.append(self)

        dummy = TaskCodeLocation(file="unknown", line=1)
        self.code_location = code_location or dummy

        self.soft_validate_task()
        self.included_from: Module | None = included_from

    def __call__(self, *args: list[Any], **kwargs: Any) -> Any:
        """Call the task."""
        return self.func(*args, **kwargs)

    @property
    def name(self) -> str:
        """Return the name of the task, including all task namespaces and group namespace."""
        return self._get_full_task_name()

    @property
    def aliases(self) -> list[str]:
        """Return the aliases of the task, prefixed with any namespaces."""
        out = []
        for alias in self._aliases:
            if self.group.alias_namespace:
                ns_alias = self.group.alias_namespace + alias
            else:
                ns_alias = alias
            out += [ns_alias]
        return out

    @property
    def groups(self) -> list[Group]:
        """Return all parent groups."""
        return self.get_all_parent_groups()

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
                text += " Attempting to run this task will fail."
            utils.print_warning(text)

    def is_hidden(self) -> bool:
        """Return True if the task is hidden.

        Being in a hidden group does not, by itself, quality task as being hidden.
        """
        assert self.group is not None
        return self.hidden or self.func.__name__.startswith("_")

    def is_in_hidden_group(self) -> bool:
        """Return True if the task is in a hidden group."""
        assert self.group is not None

        # we must check all parents to be sure
        groups = self.get_all_parent_groups()
        for group in groups:
            if group.hidden:
                return True

        return False

    def get_all_parent_groups(self) -> list[Group]:
        """Return all parent groups."""
        out = []
        g: Group | None = self.group
        while g is not None:
            out.append(g)
            g = g.parent
        return out

    def get_base_name(self) -> str:
        """Return the base name of the task, sans namespaces.

        In most cases, you want to use 'task.name' instead of this function.
        """
        if self._name:
            out = self._name
        else:
            out = self.func.__name__.replace("_", "-")
        out.lstrip("-")  # for _private functions
        return out

    def _get_full_task_name(self) -> str:
        """Return the full name of the task, including any namespace of the group the task is in right now."""
        out = self.get_base_name()

        if self.name_namespaces:
            out = NAMESPACE_SEPARATOR.join(self.name_namespaces) + NAMESPACE_SEPARATOR + out

        if self.group.name_namespace:
            out = self.group.name_namespace + NAMESPACE_SEPARATOR + out

        return out

    def add_namespace_from_group(self, group: Group) -> None:
        """Copy the namespace from the  group into the task.

        Used for copied tasks to preservs namespace of the old group)
        """
        if group.name_namespace:
            self.name_namespaces = [group.name_namespace, *self.name_namespaces]
        if group.alias_namespace:
            new_aliases = []
            for alias in self._aliases:
                new_aliases.append(group.alias_namespace + alias)
            self._aliases = new_aliases

    def add_namespace(self, namespace: str = "", alias_namespace: str = "") -> None:
        """Add a namespace to the task."""
        if namespace:
            self.name_namespaces = [namespace, *self.name_namespaces]

        new_aliases = []
        for alias in self._aliases:
            new_aliases.append(alias_namespace + alias)
        self._aliases = new_aliases

    def get_all_task_names(self) -> list[str]:
        """Return all (namespaced) names of the task which can be used on the CLI to call it, including aliases."""
        out = [self._get_full_task_name()]
        out += self.aliases
        return out

    def get_summary_line(self) -> str:
        """Return the first line of docstring, or empty string if no docstring."""
        extra_summary = " ".join(self._extra_summary)

        basic_summary = ""
        if self._desc:
            basic_summary = self._desc
        elif self.func.__doc__ is not None:
            basic_summary = self.func.__doc__.split("\n")[0]

        if basic_summary and extra_summary:
            basic_summary += " " + extra_summary
        elif extra_summary:
            basic_summary = extra_summary
        return basic_summary

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
        name = self._get_full_task_name()
        from .dispatching import dispatch

        if isinstance(args, str):
            args = [args]

        module = utils.get_callers_module()
        if args:
            res = dispatch([name, *args], sysexit_on_user_error=sysexit_on_user_error, module=module)
        else:
            res = dispatch([name], sysexit_on_user_error=sysexit_on_user_error, module=module)
        return res

    def get_top_level_group(self) -> Group | None:
        """Return the top-most group.

        Used when listing tasks to determine top-most groups from list of filtered tasks.
        """
        g = self.group
        while g is not None:
            if g.parent is None:
                return g
            g = g.parent
        return None

    def copy(self, group: Group, included_from: Module | None) -> "Task":
        """Return a copy of the task."""
        new_task = Task(
            func=self.func,
            group=group,
            included_from=included_from,
        )
        for prop in self.__dict__:
            # TODO explicit copy of some objects, code_location
            props_to_skip = [
                "func",  # passed to constructor
                "params",
                "group",  # created from func in constructor  # passed to constructor
                "included_from",  # passed to constructor
            ]
            if prop in props_to_skip:
                continue
            # For everything else shallow copy should be good enough here
            setattr(new_task, prop, getattr(self, prop))

        return new_task

    def __repr__(self) -> str:
        return f"Task(name={self.name!r}, group={self.group.name!r}, important={self.important}, hidden={self.hidden})"

    def has_supported_type(self) -> str:
        """TODO: in the future we could ass validation for function signatures.

        (I.e. if we ever find any not working, and need to explicitly prevent using them)
        """
        return "ok"

    def debug(self, fun:Callable[[Any],Any]|None=None):
        """Print detailed debug info about this object."""
        if not fun:
            fun = print

        for field in self.__dict__:
            value = getattr(self, field)

            if field == "params":
                fun(f"  {field}:")
                for param in value:
                    param: Parameter = param
                    fun(f"  param '{param.name}'")
                    fun(f"    {param.metadata=}")
                    fun(f"    {param.arg_annotation=}")
                    fun(f"    {param.kind=}")
                    fun(f"    {param.help=}")
                    fun(f"    {param.default=}")
            elif field == "func":
                fun(f"  {field}:")
                fun(f"     {value.__name__}")

            else:
                fun(f"  {field}: {value}")


def _get_wrapper(  # noqa: C901
    func: AnyFunction,
    change_dir: bool = True,
    # ----------
    group: Group | None = None,
    hidden: bool = False,
    prefix: str = "",
    important: bool = False,
    aliases: Iterable[str] | None = None,
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
        group = get_current_group(module_which_defines_task)
    assert isinstance(group, Group), f"Expected group to be a Group, got {group!r}"

    if isinstance(aliases, str):
        aliases = [aliases]

    from taskcli import tt

    # DecoratedFunction
    @functools.wraps(func)
    def wrapper_for_changing_directory(*args: list[Any], **kwargs: dict[str, Any]) -> Any:
        tt.get_runtime().current_tasks.append(task)
        from taskcli import tasktools

        breadcrumbs = tasktools.get_task_breadcrumbs()
        try:
            if tt.config.print_task_start_message:
                width = 80
                if os.isatty(sys.stderr.fileno()):
                    width = os.get_terminal_size().columns
                msg = f"―― taskcli [{breadcrumbs}] ―――――――――――".ljust(width, "―")
                utils.print_to_stderr(msg)

            if change_dir:
                with utils.change_dir(task.get_taskfile_dir()):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        finally:
            if tt.config.print_task_start_message:
                black = configuration.colors.dark_gray
                clear = configuration.colors.end
                msg = f"{black}――{clear}"
                utils.print_to_stderr(msg, color="")
            tt.get_runtime().current_tasks.pop()

    del kwargs["group"]
    del kwargs["aliases"]
    del kwargs["env"]

    task: Task = Task(wrapper_for_changing_directory, env=env, group=group, aliases=aliases, **kwargs)

    if not hasattr(module_which_defines_task, "decorated_functions"):
        module_which_defines_task.decorated_functions = []  # type: ignore[attr-defined]

    # Ensure no double decoration
    for atask in module_which_defines_task.decorated_functions:
        if atask.func == func:
            msg = f"Function {func} is already decorated as a task"
            raise ValueError(msg)

    # Ensure no task with this name already exist
    for atask in module_which_defines_task.decorated_functions:
        if atask.name == task.name:
            msg = (
                f"A task with this name {task.name} already exists in this module "
                f"{module_which_defines_task.__name__=} {module_which_defines_task.__file__=}."
                "You might be seeing this due to a circular import, if so, try moving any tt.include(module) calls to "
                "after any @task declarations."
            )
            raise ValueError(msg)

    module_which_defines_task.decorated_functions.append(task)

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
