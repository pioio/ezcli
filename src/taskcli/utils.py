import contextlib
import os
import re
import sys
import typing

import taskcli

from . import configuration

ENDC = configuration.get_end_color()
UNDERLINE = configuration.get_underline()

def print_stderr(text: str) -> None:
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


def reset_tasks() -> None:
    """Clear the list of tasks."""
    # clear included tasks
    from . import core

    core.get_runtime().tasks = []
    taskcli.group.DEFAULT_GROUP.tasks = []
    taskcli.group.created.clear()

    # clear tasks in each module
    for module in sys.modules.values():
        if hasattr(module, "decorated_functions"):
            module.decorated_functions = []  # type: ignore[attr-defined]


def get_root_module() -> str:
    """Return the name of the module of the runtime."""
    return sys.modules["__main__"].__name__


def some_test_function(a: int, b: int) -> None:
    """Test function, ignore it."""
    print("Hello from inside taskcli:", str(a + b))  # noqa: T201
