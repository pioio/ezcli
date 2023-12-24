from typing import Annotated as ann  # noqa: N813
from typing import Any, Iterable, Sequence

import taskcli

from . import configuration, utils
from .annotations import Arg
from .configuration import config
from .core import extra_args, extra_args_list, include
from .parameter import Parameter
from .parser import dispatch
from .task import task
from .utils import get_runtime
from . import listing
# from . import taskcli taskclimodule


def hide_group(group: str) -> None:
    """Hide a group from the help message."""
    utils.get_runtime().hidden_groups.append(group)


def arg(
    typevar: Any,
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
) -> Any:
    kwargs = locals()
    del kwargs["help"]
    del kwargs["typevar"]
    return ann[typevar, help, Arg(**kwargs)]


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
]
