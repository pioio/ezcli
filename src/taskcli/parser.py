import argparse
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

        signature = inspect.signature(dfunc.func)
        for param in signature.parameters.values():
            _add_param_to_subparser(param, subparser)

    return root_parser

def _add_param_to_subparser(param:inspect.Parameter, subparser:argparse.ArgumentParser) -> None:

        param_has_a_default = param.default is not inspect.Parameter.empty
        param_has_annotation = param.annotation is not inspect.Parameter.empty
        param_using_typing_annotated =  getattr(param.annotation, "__metadata__", None) is not None

        args = []
        kwargs = {}
        name = _build_parser_name(param)

        # Default value is either in the param, or in the annotation
        # The default value from param takes precedence
        if param.default is not inspect.Parameter.empty:
            kwargs['default'] = param.default
        else:
            if param_has_annotation and param_using_typing_annotated:
                for data in param.annotation.__metadata__:
                    if isinstance(data, annotations.Arg):
                        if data.default is not annotations.Empty:
                            kwargs['default'] = data.default
                        break


        #kwargs['default'] = _build_parser_default(param)

        default_value = kwargs['default'] if 'default' in kwargs else None
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if param_has_a_default:
                kwargs['nargs'] = '?'
            else:
                kwargs['nargs'] = 1

        if param_has_annotation:
            thetype = param.annotation if not param_using_typing_annotated else param.annotation.__origin__
            if thetype is not inspect.Parameter.empty:
                if thetype is bool:
                    if default_value is None:
                        kwargs['action'] = "store_true"
                    else:
                        if default_value:
                            kwargs['action'] = "store_false"
                        else:
                            kwargs['action'] = "store_true"

        new_kwargs = {}
        if param_has_annotation and param_using_typing_annotated:
            metadata = param.annotation.__metadata__

            for data in metadata:
                if isinstance(data, str):
                    kwargs["help"] = metadata[0]

                if isinstance(data, annotations.Help):
                    kwargs["help"] = data.text
                if isinstance(data, annotations.Choice):
                    kwargs["choices"] = data.text
                if isinstance(data, annotations.Arg):
                    new_kwargs = data.get_argparse_fields()
                    if "default" in new_kwargs:
                        del new_kwargs["default"] # we used it above
                    # pass to argparse
                    kwargs.update(new_kwargs)
            #print("zzzzzz ", dfunc.func.__name__)


        #print(f"Adding argument {name} with kwargs {kwargs}")
        subparser.add_argument(name, **kwargs)
            #

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
