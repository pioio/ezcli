import contextlib
import os
import re
import sys

import typing

import taskcli

from .types import Module

from . import configuration, constants

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

def get_current_module(offset) -> Module:
    """Return the module of the caller.

    Args:
        offset (int): 0 for the current module (invalid), 1 for the caller of this function, 2 for the caller's caller,

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
    """Returns the list of tasks imported from other modules."""
    raise NotImplementedError("TODO: implement this")

def get_all_tasks() -> list["Task"]:
    """Return the list of all tasks imported into the runtime."""
    from .core import get_runtime
    return get_runtime().tasks

def get_tasks(module:Module|None=None) -> list["Task"]:
    """Return the list of all tasks defined in the specified module. Can be used to customize many tasks at ones.

    If no module is specified, the module of the caller is used.

    This function should be called after all tasks are defined (after @task decorator has been used in that module).

    In practice inless you explicitlu specify a module, this function must only be called
    from the ./tasks.py file defining the tasks.

    TODO: consider allowing it to return included tasks as well.

    Example:
        ```
        @task
        def deploy_to_prod()
            pass

        tasks:list[Task] = tt.get_tasks()
        for t in tasks:
            if "prod" in t.name:
                t.important = True
        ```
    """
    if module is None:
        module = get_current_module(offset=2)

    module_path = module.__file__
    if hasattr(module, "decorated_functions") and len(module.decorated_functions):
        return module.decorated_functions
    else:
        print_error(f"get_tasks(): No tasks found in the current module ({module_path}). "
                    "Make sure to use the @task decorator first.")
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

    # Clear global configuration (some tests might modify it)
    from taskcli import tt
    from taskcli.taskcliconfig import TaskCLIConfig

    new_config = TaskCLIConfig(load_from_env=False)
    for key, value in new_config.__dict__.items():
        setattr(tt.config, key, value)


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
