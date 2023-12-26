import contextlib
import os
import re
import sys
import typing

import taskcli

from . import configuration

if typing.TYPE_CHECKING:
    from taskcli.taskcli import TaskCLI

    from .task import Task


ENDC = configuration.get_end_color()
UNDERLINE = configuration.get_underline()


def print_err(text: str) -> None:
    """Print to stderr."""
    GREEN = configuration.colors.green
    text = f"{GREEN}{text}{ENDC}"

    print(text, file=sys.stderr, flush=True)  # noqa: T201


def print_warning(text: str) -> None:
    """Print yellow text to stderr."""
    YELLOW = configuration.colors.yellow
    text = f"{YELLOW}{text}{ENDC}"
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


def reset_tasks() -> None:
    """Clear the list of tasks."""
    # clear included tasks
    taskcli.utils.get_runtime().tasks = []
    taskcli.group.DEFAULT_GROUP.tasks = []
    taskcli.group.created.clear()

    # clear tasks in each module
    for module in sys.modules.values():
        if hasattr(module, "decorated_functions"):
            module.decorated_functions = []  # type: ignore[attr-defined]


def get_tasks() -> list["Task"]:
    """Return the list of tasks."""
    return taskcli.utils.get_runtime().tasks


def get_root_module() -> str:
    """Return the name of the module of the runtime."""
    return sys.modules["__main__"].__name__


def get_runtime() -> "TaskCLI":
    """Return the TaskCLI runtime."""
    return taskcli.core.task_cli


def some_test_function(a: int, b: int) -> None:
    """Test function, ignore it."""
    print("Hello from inside taskcli:", str(a + b))  # noqa: T201
