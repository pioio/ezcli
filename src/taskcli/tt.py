"""Exposes all the commonly used functions and classes.

This module is the public API of the library.

Example:
```
    from taskcli import task, run, tt

    @task
    def foobar():
        run("date")
```

"""


from . import core
from .arg import arg
from .core import get_extra_args, get_extra_args_list, get_runtime, include
from .group import Group
from .parameter import Parameter
from .parser import dispatch
from .runcommand import run
from .task import Task, task
from .taskcliconfig import runtime_config as config
from .types import Any, AnyFunction, Module
from .utils import get_tasks

__all__ = ["config"]
