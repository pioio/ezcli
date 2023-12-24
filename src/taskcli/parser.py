import argparse
from email.policy import default
import inspect
import logging
import re
import sys
import typing
from ast import Store, arg

from . import annotations
from .decoratedfunction import Task
from .types import AnyFunction
from .utils import param_to_cli_option
from .listing import list_tasks
import taskcli
""""
TODO:
  auto-aliases for commands

"""

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s|  %(message)s')

import os

def dispatch(argv:list[str]|None=None) -> None:
    decorated_function:list[Task] = taskcli.get_runtime().tasks

    parser = build_parser(decorated_function)
    # support argcomplete
    #if "argcomplete" in sys.modules:
    if "_ARGCOMPLETE" in os.environ:
        import argcomplete
        print("Starting completion") # for unit tests
        argcomplete.autocomplete(parser)
        # it will exit if it's a completion request

    argv = argv or sys.argv[1:]

    from .core import _extract_extra_args
    argv = _extract_extra_args(argv, taskcli.get_runtime())

    argconfig = parser.parse_args(argv)

    if argconfig.version:
        print("version info...")
        sys.exit(0)

    if hasattr(argconfig, "task"):
        for dfunc in decorated_function:
            if dfunc.get_full_task_name() == argconfig.task:
                signature = inspect.signature(dfunc.func)
                kwargs = {}
                for param in signature.parameters.values():
                    name = param.name.replace("_", "-")
                    kwargs[name] = getattr(argconfig, name)
                dfunc.func(**kwargs)
                return None

        print(f"Task {argconfig.task} not found")
        sys.exit(1)
    else:

        lines = list_tasks(decorated_function, verbose=3)
        for line in lines:
            print(line)


    #print("done")
    #log.info("done" + str(argconfig))

    return None



def build_parser(decorated_function:list[Task]) -> argparse.ArgumentParser:
    root_parser = argparse.ArgumentParser()

    # Main parsers
    root_parser.add_argument("--version", action="store_true")

    subparsers = root_parser.add_subparsers(help='Task to run')

    for dfunc in decorated_function:
        subparser = subparsers.add_parser(dfunc.get_full_task_name())
        subparser.set_defaults(task=dfunc.get_full_task_name())

        for param in dfunc.params:
            _add_param_to_subparser(param, subparser)
        # signature = inspect.signature(dfunc.func)
        # for param in signature.parameters.values():
        #     _add_param_to_subparser(param, subparser)

    return root_parser

from .parameter import Parameter

def _add_param_to_subparser(param:Parameter, subparser:argparse.ArgumentParser) -> None:
    args = param.get_argparse_names()
    kwargs = {}

    if param.has_default():
        kwargs['default'] = param.default
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            kwargs['nargs'] = '?'

    if param.type is bool:
        if param.has_default():
            if param.default:
                kwargs['action'] = "store_false"
            else:
                kwargs['action'] = "store_true"
        else:
            kwargs['action'] = "store_true"

    if param.help:
        kwargs['help'] = param.help

    # TODO:
    # if param.metavar:
    #     kwargs['metavar'] = param.metavar
    subparser.add_argument(*args, **kwargs)



def _build_parser_name(param:inspect.Parameter) -> str:
    if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
        name = param.name.replace("_", "-")
    else:
        name = param_to_cli_option(param.name)
    return name

def _build_parser_default(param:inspect.Parameter) -> str|None:
    if param.default is inspect.Parameter.empty:
        return None
    else:
        return param.default
