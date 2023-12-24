
from dataclasses import dataclass

from . import configuration
from .configuration import config
from .core import extra_args, extra_args_list, include
from .core import run as run_task
from .task import task

from typing import Any
from typing import Annotated as ann
from .parser import dispatch
from .annotations import Arg
from .annotations import Arg as arg

__all__ = ["task", "include", "run_task", "configuration", "config", "extra_args", "extra_args_list", "Arg", ann]
