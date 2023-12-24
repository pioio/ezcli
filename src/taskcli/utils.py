import sys
import taskcli

import typing
if typing.TYPE_CHECKING:
    from .decoratedfunction import Task
    from taskcli.taskcli import TaskCLI


from . import configuration
import re

def strip_escape_codes(s:str) ->str :

    ENDC = configuration.get_end_color()
    UNDERLINE = configuration.get_underline()

    return re.sub(r"\033\[[0-9;]*m", "", s).replace(ENDC, "").replace(UNDERLINE, "")


def param_to_cli_option(arg:str) -> str:
    """Convert foo_bar to --foo-bar, and g to -g"""
    if len(arg) == 1:
        return "-" + arg.replace("_", "-")
    else:
        return "--" + arg.replace("_", "-")


def reset_tasks():
    """Clear the list of tasks"""
    # clear included tasks
    taskcli.utils.get_runtime().tasks = []

    # clear tasks in each module
    for module in sys.modules.values():
        if hasattr(module, "decorated_functions"):
            module.decorated_functions = [] # type: ignore



def get_tasks() -> list["Task"]:
    """Return the list of tasks"""
    return taskcli.utils.get_runtime().tasks

def get_root_module() -> str:
    return sys.modules["__main__"].__name__


def get_runtime() -> "TaskCLI":
    return taskcli.core.task_cli