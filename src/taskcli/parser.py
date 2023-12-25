import argparse
import inspect
import logging
import os
import sys
from typing import Any

import taskcli

from .listing import list_tasks
from .parameter import Parameter
from .task import Task
from .taskcli import TaskCLI
from .types import AnyFunction
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


def dispatch(argv: list[str] | None = None) -> None:  # noqa: C901
    """Dispatch the command line arguments to the correct function."""
    tasks: list[Task] = taskcli.get_runtime().tasks

    parser = build_parser(tasks)

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
    if argconfig.show_hidden:
        taskcli.config.show_hidden_tasks = True
        taskcli.config.show_hidden_groups = True

    if argconfig.list:
        print_listed_tasks(tasks, verbose=argconfig.list)
        sys.exit(0)

    def _dispatch(fun: AnyFunction):
        signature = inspect.signature(task.func)
        kwargs = {}
        for param in signature.parameters.values():
            name = param.name.replace("_", "-")
            kwargs[name] = getattr(argconfig, name)
        return task.func(**kwargs)


    if hasattr(argconfig, "task"):
        for task in tasks:
            if task.get_full_task_name() == argconfig.task:
                return _dispatch(task.func)

        # Not found, search aliases
        for task in tasks:
            if argconfig.task in task.aliases:
                return _dispatch(task.func)

        print(f"Task {argconfig.task} not found")  # noqa: T201
        sys.exit(1)
    else:
        print_listed_tasks(tasks, verbose=1)

    return None


def print_listed_tasks(tasks: list[Task], verbose: int) -> None:
    """Print the listed tasks."""
    lines = list_tasks(tasks, verbose=verbose)
    for line in lines:
        print(line)  # noqa: T201


def build_parser(decorated_function: list[Task]) -> argparse.ArgumentParser:
    """Build the parser."""
    root_parser = argparse.ArgumentParser()

    # Main parsers
    root_parser.add_argument("--version", action="store_true")
    root_parser.add_argument(
        "-l", "--list", action="count", default=0, help="List tasks, use -ll and -lll for more info"
    )
    root_parser.add_argument("--show-hidden", "-H", action="store_true", default=False)

    subparsers = root_parser.add_subparsers(help="Task to run")

    for dfunc in decorated_function:
        all_names_of_task = dfunc.get_all_task_names()

        for name in all_names_of_task:
            subparser = subparsers.add_parser(name)
            subparser.set_defaults(task=name)

            for param in dfunc.params:
                _add_param_to_subparser(param, subparser)

    return root_parser


def _add_param_to_subparser(param: Parameter, subparser: argparse.ArgumentParser) -> None:
    args = param.get_argparse_names()
    kwargs: dict[str, Any] = {}

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
        assert isinstance(param.default, str) or param.default is None
        return param.default
