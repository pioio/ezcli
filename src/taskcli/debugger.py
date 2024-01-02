from typing import Any, Callable
from .task import Task
from .taskcliconfig import TaskCLIConfig



def debug(obj:Task|TaskCLIConfig, fun:Callable[[str],Any]=print):
    """Print debug info about a task or the current config."""
    obj.debug(fun)

