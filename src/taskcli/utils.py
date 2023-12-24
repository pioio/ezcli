import sys
import taskcli
from .decoratedfunction import DecoratedFunction

def param_to_cli_option(arg:str) -> str:
    """Convert foo_bar to --foo-bar, and g to -g"""
    if len(arg) == 1:
        return "-" + arg.replace("_", "-")
    else:
        return "--" + arg.replace("_", "-")


def reset_tasks():
    """Clear the list of tasks"""
    main_module = sys.modules["__main__"]
    main_module.decorated_functions = [] # type: ignore[attr-defined]

def get_tasks() -> list[DecoratedFunction]:
    """Return the list of tasks"""
    main_module = sys.modules["__main__"]
    if "decorated_functions" not in main_module.__dir__():
        # add decorated_functions to module
        return []
    else:
        return main_module.decorated_functions # type: ignore[attr-defined]

def get_root_module() -> str:
    return sys.modules["__main__"].__name__

import taskcli.core
from taskcli.taskcli import TaskCLI

def get_taskcli() -> TaskCLI:
    return taskcli.core.task_cli