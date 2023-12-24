import argparse
import inspect
import logging
import os
import sys

import taskcli

from .decoratedfunction import Task
from .listing import list_tasks
from .parameter import Parameter
from .taskcli import TaskCLI
from .utils import param_to_cli_option

""""
TODO:
  auto-aliases for commands

"""

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s|  %(message)s")


def _extract_extra_args(argv: list[str], task_cli: TaskCLI) -> list[str]:
    first_double_hyphen = argv.index("--") if "--" in argv else -1
    if first_double_hyphen == -1:
        return argv
    else:
        task_cli.extra_args_list = argv[first_double_hyphen + 1 :]
        return argv[:first_double_hyphen]


def dispatch(argv: list[str] | None = None) -> None:
    """Dispatch the command line arguments to the correct function."""
    decorated_function: list[Task] = taskcli.get_runtime().tasks

    parser = build_parser(decorated_function)

    if "_ARGCOMPLETE" in os.environ:
        import argcomplete

        print("Starting completion")  # for unit tests # noqa: T201
        argcomplete.autocomplete(parser)
        # it will exit if it's a completion request

    argv = argv or sys.argv[1:]

    argv = _extract_extra_args(argv, taskcli.get_runtime())

    argconfig = parser.parse_args(argv)

    if argconfig.version:
        print("version info...")  # noqa: T201
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

        print(f"Task {argconfig.task} not found")  # noqa: T201
        sys.exit(1)
    else:
        lines = list_tasks(decorated_function, verbose=3)
        for line in lines:
            print(line)  # noqa: T201

    return None


def build_parser(decorated_function: list[Task]) -> argparse.ArgumentParser:
    root_parser = argparse.ArgumentParser()

    # Main parsers
    root_parser.add_argument("--version", action="store_true")

    subparsers = root_parser.add_subparsers(help="Task to run")

    for dfunc in decorated_function:
        subparser = subparsers.add_parser(dfunc.get_full_task_name())
        subparser.set_defaults(task=dfunc.get_full_task_name())

        for param in dfunc.params:
            _add_param_to_subparser(param, subparser)

    return root_parser


def _add_param_to_subparser(param: Parameter, subparser: argparse.ArgumentParser) -> None:
    args = param.get_argparse_names()
    kwargs = {}

    if param.has_default():
        kwargs["default"] = param.default
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            kwargs["nargs"] = "?"

    if param.type is bool:
        if param.has_default():
            if param.default:
                kwargs["action"] = "store_false"
            else:
                kwargs["action"] = "store_true"
        else:
            kwargs["action"] = "store_true"

    if param.help:
        kwargs["help"] = param.help

    subparser.add_argument(*args, **kwargs)


def _build_parser_name(param: inspect.Parameter) -> str:
    if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
        name = param.name.replace("_", "-")
    else:
        name = param_to_cli_option(param.name)
    return name


def _build_parser_default(param: inspect.Parameter) -> str | None:
    if param.default is inspect.Parameter.empty:
        return None
    else:
        return param.default
