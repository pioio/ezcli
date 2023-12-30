import contextlib
import logging
import os
import re
import sys
import typing

import taskcli

from .logging import get_logger
from . import configuration, constants
from .types import Module
log = get_logger(__name__)

ENDC = configuration.get_end_color()
UNDERLINE = configuration.get_underline()


def print_stderr(text: str) -> None:
    """Print string to stderr, unmodified."""
    print(text, file=sys.stderr, flush=True)  # noqa: T201


def print_err(text: str) -> None:
    """Print to stderr."""
    GREEN = configuration.colors.green
    text = f"{GREEN}{text}{ENDC}"

    print(text, file=sys.stderr, flush=True)  # noqa: T201


def print_error(text: str) -> None:
    """Print error to stderr."""
    RED = configuration.colors.red
    text = f"{RED}taskcli: Error: {text}{ENDC}"

    print(text, file=sys.stderr, flush=True)  # noqa: T201


def print_warning(text: str) -> None:
    """Print yellow text to stderr."""
    YELLOW = configuration.colors.yellow
    text = f"{YELLOW}taskcli: Warning: {text}{ENDC}"
    print(text, file=sys.stderr, flush=True)  # noqa: T201



@contextlib.contextmanager
def change_dir(path: str) -> typing.Iterator[None]:
    """Context manager to change the current working directory."""
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


def strip_escape_codes(s: str) -> str:
    """Remove ANSI escape codes from a string. So, removes colors, underlines, etc."""
    out = re.sub(r"\033\[[0-9;]*m", "", s).replace(ENDC, "").replace(UNDERLINE, "")

    return out


def param_to_cli_option(arg: str) -> str:
    """Convert foo_bar to --foo-bar, and g to -g."""
    if len(arg) == 1:
        return "-" + arg.replace("_", "-")
    else:
        return "--" + arg.replace("_", "-")


if typing.TYPE_CHECKING:
    from .task import Task


def get_callers_module() -> Module:
    offset = 3
    return get_module(offset=offset)


def get_module(offset: int) -> Module:
    """Return the module of the caller.

    Args:
        offset (int): 0 - invalid, 1 for the caller of this function, 2 for the caller's caller,

    Example:
            when calling from ./tasks,py, use offset=1.
            when calling from a taskcli.utils, which was called from ./tasks.py, use offset=2.
    """
    import inspect

    assert offset >= 1

    frame = inspect.currentframe()
    for _ in range(offset):
        assert frame is not None
        frame = frame.f_back
        assert frame is not None

    module = inspect.getmodule(frame)
    assert module is not None
    return module


def get_imported_tasks() -> list["Task"]:
    """Return the list of tasks imported from other modules."""
    msg = "TODO: implement this"
    raise NotImplementedError(msg)


def get_task(name: str) -> "Task":
    """Get task from the current module by name."""
    module = get_callers_module()
    tasks = get_tasks(module=module)
    d = {t.name: t for t in tasks}
    from .task import UserError

    if name not in d:
        msg = f"get_task(): Task '{name}' not found in module {module.__file__}"
        raise UserError(msg)
    return d[name]


def get_tasks_dict() -> dict[str, "Task"]:
    """Get all tasks in the current module as a dictionary."""
    module = get_callers_module()
    tasks = get_tasks(module=module)
    return {t.name: t for t in tasks}


def get_tasks(module: Module | None = None, also_included: bool = True) -> list["Task"]:
    """Return the list of all tasks defined in the specified module. Including any included tasks.

    If no module is specified, the module of the caller is used.

    This function should be called after all tasks are defined (after @task decorator has been used in that module).

    In practice inless you explicitlu specify a module, this function must only be called
    from the ./tasks.py file defining the tasks.


    Example:
        ```
        @task
        def deploy_to_prod()
            pass

        tt.include(somemodule.somefunction)

        tasks:list[Task] = tt.get_tasks()
        assert len(tasks) == 2
        for t in tasks:
            if "prod" in t.name:
                t.important = True
        ```
    """
    if module is None:
        module = get_module(offset=2)

    module_path = module.__file__
    if hasattr(module, "decorated_functions") and len(module.decorated_functions):
        out = []
        for task in module.decorated_functions:
            if task.included_from and not also_included:
                # skipping included tasks
                continue
            out.append(task)

        return out
    else:
        print_error(
            f"get_tasks(): No tasks found in the current module ({module_path}). "
            "Make sure to use the @task decorator first."
        )
        sys.exit(1)


def reset_tasks() -> None:
    """Clear the list of tasks and the entire context."""
    # clear included tasks
    from . import core

    core.get_runtime().tasks = []
    taskcli.group.DEFAULT_GROUP.tasks = []
    taskcli.group.created.clear()

    # Clear tasks in each module
    for module in sys.modules.values():
        if hasattr(module, "decorated_functions"):
            module.decorated_functions = []  # type: ignore[attr-defined]
        if hasattr(module, "taskcli_top_level_groups"):
            module.taskcli_top_level_groups = []

    # Clear global configuration (some tests might modify it)
    from taskcli import tt
    from taskcli.taskcliconfig import TaskCLIConfig

    new_config = TaskCLIConfig(load_from_env=False)
    for key, value in new_config.__dict__.items():
        setattr(tt.config, key, value)

    # # reset any logging configuration set by previous tests
    assert tt.config.verbose == 0
    from .logging import configure_logging
    configure_logging()


def get_basename() -> str:
    """Return the name of the taskcli executable."""
    return os.path.basename(sys.argv[0])


def is_basename_tt() -> bool:
    """Return the name of the taskcli executable."""
    return get_basename() == constants.TT_COMMAND_NAME


def get_root_module() -> str:
    """Return the name of the module of the runtime."""
    return sys.modules["__main__"].__name__


def some_test_function(a: int, b: int) -> None:
    """Test function, ignore it."""
    print("Hello from inside taskcli:", str(a + b))  # noqa: T201


def assert_no_dup_by_name(container: list[typing.Any]) -> None:
    """Assert that there are no duplicates in the list by name."""
    seen = []
    for item in container:
        assert item.name not in seen
        seen.append(item.name)
