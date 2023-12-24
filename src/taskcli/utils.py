import sys
import taskcli
from .decoratedfunction import Task

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
            module.decorated_functions = []



def get_tasks() -> list[Task]:
    """Return the list of tasks"""
    return taskcli.utils.get_runtime().tasks

def get_root_module() -> str:
    return sys.modules["__main__"].__name__

import taskcli.core
from taskcli.taskcli import TaskCLI

def get_runtime() -> TaskCLI:
    return taskcli.core.task_cli