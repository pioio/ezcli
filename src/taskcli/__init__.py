# from . import taskcli taskclimodule
from typing import Annotated, Any, Iterable, Sequence, TypeVar

import taskcli

from . import configuration, listing, utils
from .annotations import Arg
from .configuration import config
from .core import extra_args, extra_args_list, include
from .group import Group
from .parameter import Parameter
from .parser import dispatch
from .task import task
from .utils import get_runtime
from .task import Task

from typing import Annotated as ann  # noqa: N813 # isort: skip


def hide_group(group: str) -> None:
    """Hide a group from the help message."""
    utils.get_runtime().hidden_groups.append(group)


T = TypeVar("T")


def arg(
    typevar: T,
    help: str | None = None,
    /,
    # Specific to taskcli
    important: bool = False,
    # forwarded to argparse
    action: str | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | None = None,
    nargs: str | int | None = None,
    default: Any = Parameter.Empty,
) -> Annotated[T, str, Arg]:
    kwargs = locals()

    del kwargs["help"]
    del kwargs["typevar"]
    return Annotated[typevar, help, Arg(**kwargs)]  # type: ignore # noqa: PGH003


__all__: Sequence[str] = [
    "task",
    "include",
    "utils",
    "configuration",
    "config",
    "extra_args",
    "extra_args_list",
    "Arg",
    "ann",
    "get_runtime",
    "dispatch",
    "listing",
    "Annotated",
    "Group",
    "Task",
]
