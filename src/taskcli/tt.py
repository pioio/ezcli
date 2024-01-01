"""The public API of taskcli library.

Objects exposed via this module change rarely, and are reasonably well documented.

Example:
```
    # Recommended usage:
    #  - `task` and `run` are used often, so import them directly
    #  - `tt` contains all the other public API functions and Object you might need
    from taskcli import task, run, tt
    @task
    def mytask():
        run("date")

    # Alternative usage
    from taskcli import tt
    @tt.task
    def mytask():
        tt.run("date")
```

"""

from . import core
from .arg import arg
from .core import get_extra_args, get_extra_args_list, get_runtime
from .group import Group
from .include import include, include_function, include_module
from .main import main
from .parameter import Parameter
from .dispatching import dispatch
from .runcommand import run
from .task import Task
from .task import task_decorator as task
from .taskcliconfig import runtime_config as config
from .types import Any, AnyFunction, Module
from .utils import get_task, get_tasks, get_tasks_dict

__all__ = ["config", "Task", "get_runtime"]
