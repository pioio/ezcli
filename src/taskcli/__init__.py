
from dataclasses import dataclass
from argh import arg  # type: ignore[import]

from . import configuration
from .configuration import config
from .core import extra_args, extra_args_list, include
from .core import run as run_task
from .task import task

from typing import Any

from .parser import dispatch
from .annotations import Arg

__all__ = ["task", "include", "arg_optional", "run_task", "arg", "configuration", "config", "extra_args", "extra_args_list"]
