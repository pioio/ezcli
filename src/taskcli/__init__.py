
from ast import Param
from dataclasses import dataclass
from typing import Annotated as ann, Iterable
from typing import Any

from .parameter import Parameter

from . import configuration
from . import listing
from .annotations import Arg
#from .annotations import Arg as arg
from .configuration import config
from .core import extra_args, extra_args_list, include
from .core import run as run_task
from .parser import dispatch
from .task import task
from . import utils
from .utils import get_runtime
import taskcli

def hide_group(group:str):
    """Hide a group from the help message"""
    taskcli.utils.get_runtime().hidden_groups.append(group)

def arg(typevar,  help:str|None=None, /,
        # Specific to taskcli
        important:bool=False,

        # forwarded to argparse
        action:str|None=None,
        choices:Iterable[Any]|None=None,
        metavar:str|None=None,
        nargs:str|int|None=None,
        default:Any=Parameter.Empty,
        ):
    kwargs = locals()
    del kwargs["help"]
    del kwargs["typevar"]
    return ann[typevar, help, Arg(**kwargs)]


__all__ = ["task", "include", "run_task", "configuration", "config", "extra_args", "extra_args_list", "Arg", ann, "get_runtime"]
