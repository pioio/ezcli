# from . import taskcli taskclimodule
from typing import Annotated, Any, Iterable, Sequence, TypeVar

import taskcli
import taskcli.core

from . import configuration, examples, listing, utils
from .annotations import Arg
from .arg import arg
from .configuration import config
from .core import get_extra_args, get_extra_args_list, get_runtime, include
from .group import Group
from .parameter import Parameter
from .parser import dispatch
from .runcommand import run
from .task import Task, task

from typing import Annotated as ann  # noqa: N813 # isort: skip


def hide_group(group: str) -> None:
    """Hide a group from the help message."""
    taskcli.core.get_runtime().hidden_groups.append(group)


__all__: Sequence[str] = [
    "task",
    "include",
    "utils",
    "configuration",
    "config",
    "get_extra_args",
    "get_extra_args_list",
    "Arg",
    "ann",
    "get_runtime",
    "dispatch",
    "listing",
    "Annotated",
    "Group",
    "Task",
    "run",
    "tt",
]
