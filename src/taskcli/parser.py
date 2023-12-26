import argparse
import inspect
import logging
import os
import sys
from typing import Any

import taskcli

from . import envvars, examples, taskfiledev
from .init import create_tasks_file
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


GROUP_SUFFIX = "[group]"  # TODO: change this later

log = logging.getLogger(__name__)

if "-v" in sys.argv or "--verbose" in sys.argv:
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s|  %(message)s")
else:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s|  %(message)s")


def _extract_extra_args(argv: list[str], task_cli: TaskCLI) -> list[str]:
    first_double_hyphen = argv.index("--") if "--" in argv else -1
    if first_double_hyphen == -1:
        return argv
    else:
        task_cli.extra_args_list = argv[first_double_hyphen + 1 :]
        return argv[:first_double_hyphen]


def dispatch(argv: list[str] | None = None, tasks_found: bool = True) -> Any:  # noqa: C901
    """Dispatch the command line arguments to the correct function."""
    # Initial parser, only used to find the tasks file

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
    taskcli.get_runtime().parsed_args = argconfig

    if argconfig.init:
        create_tasks_file("tasks.py")
        return

    if argconfig.version:
        print("version info...")  # noqa: T201
        sys.exit(0)

    if not tasks_found:
        print_task_not_found_error()
        sys.exit(1)

    if argconfig.show_hidden:
        taskcli.config.show_hidden_tasks = True
        taskcli.config.show_hidden_groups = True

    if argconfig.list:
        print_listed_tasks(tasks, verbose=argconfig.list, ready_verbose=argconfig.ready)
        return
    if argconfig.list_all:
        print_listed_tasks(tasks, verbose=999, ready_verbose=999)
        return
    if argconfig.examples:
        examples.print_examples()
        return

    def _dispatch(task: Task) -> Any:
        kwargs = {}

        for param in task.params:
            name = param.get_argparse_names()[0].replace("-", "_")
            value = getattr(argconfig, name)
            value = _convert_types_from_str_to_function_type(param, value)
            kwargs[name] = value

        ret_value = task.func(**kwargs)
        if argconfig.print_return_value:
            print(ret_value)  # noqa: T201
        return ret_value

    ready_verbose = argconfig.ready

    if hasattr(argconfig, "task"):
        if argconfig.task.endswith(GROUP_SUFFIX):
            tasks_in_group = [
                task for task in tasks if task.group.get_name_for_cli() == argconfig.task[: -len(GROUP_SUFFIX)]
            ]

            group_name = tasks_in_group[0].group.name
            num_tasks = len(tasks_in_group)
            hidden_tasks = len([x for x in tasks_in_group if x.hidden])
            hidden_tasks_str = f" ({hidden_tasks} hidden)" if hidden_tasks > 0 else ""
            taskcli.utils.print_err(f"Tasks in group {group_name} ({num_tasks}) {hidden_tasks_str}")

            print_listed_tasks(tasks_in_group, verbose=4, ready_verbose=999)
            sys.exit(1)
        else:
            for task in tasks:
                if task.get_full_task_name() == argconfig.task:
                    return _dispatch(task)

            # Not found, search aliases
            for task in tasks:
                if argconfig.task in task.aliases:
                    return _dispatch(task)

            print(f"Task {argconfig.task} not found")  # noqa: T201
            sys.exit(1)
    else:
        print_listed_tasks(tasks, verbose=1, ready_verbose=ready_verbose)

    return None


def print_task_not_found_error() -> None:
    """Print the error message when no tasks are found."""
    # TODO, check upper dirs
    print(  # noqa: T201
        "taskcli: No tasks file found in current directory, "
        f"looked for: {envvars.TASKCLI_TASKS_PY_FILENAMES.value}. "
        f"Set the environment variable {envvars.TASKCLI_TASKS_PY_FILENAMES.name} to a comma separated "
        "list of filename to change the "
        "list of filenames to look for. See docs for details."
    )
    local_taskfile = taskfiledev.has_taskfile_dev()

    if taskfiledev.has_taskfile_dev() and not taskfiledev.should_include_taskfile_dev():
        print(  # noqa: T201
            f"taskcli: Note: found a {local_taskfile} file. "
            "See the docs on how to include and list its tasks automatically."
        )
    sys.exit(1)


def _convert_types_from_str_to_function_type(param: Parameter, value: Any) -> Any:
    if param.type is int:
        value = int(value)
    elif param.type is bool:
        # TODO
        msg = "Bool not implemented fully"
        raise Exception(msg)

    elif param.type is float:
        value = float(value)

    # list of int
    # > elif param.type is list:
    # >     if hasattr(param.type, "__args__"):
    # >         if param.type.__args__[0] is int:
    # >             value = [int(x) for x in value]
    # >         else:
    # >             raise Exception(f"Type {param.type} not implemented")
    return value


def print_listed_tasks(tasks: list[Task], verbose: int, ready_verbose: int) -> None:
    """Print the listed tasks."""
    lines = list_tasks(tasks, verbose=verbose, env_verbose=ready_verbose)
    for line in lines:
        print(line)  # noqa: T201


ARG_NO_GO_TASK = "--no-go-task"
DEFAULT_TASK_PY = envvars.TASKCLI_TASKS_PY_FILENAMES.value


def build_initial_parser() -> argparse.ArgumentParser:
    """Build the parser."""
    root_parser = argparse.ArgumentParser(add_help=False)
    _add_initial_tasks_to_parser(root_parser)
    return root_parser


def _add_initial_tasks_to_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f",
        "--file",
        required=False,
        default=DEFAULT_TASK_PY,
        help=f"Which tasks file(s) to use, comma separate, first one found is used. default is '{DEFAULT_TASK_PY}'",
    )


def build_parser(tasks: list[Task]) -> argparse.ArgumentParser:
    """Build the parser."""
    root_parser = argparse.ArgumentParser()

    # Main parsers
    root_parser.add_argument("--version", action="store_true")
    root_parser.add_argument("-v", "--verbose", action="store_true")
    root_parser.add_argument(
        "-r", "--ready", help="Show detailed info about task being ready", action="count", default=0
    )
    root_parser.add_argument(
        "-l", "--list", action="count", default=0, help="List tasks, use -ll and -lll for more info"
    )
    root_parser.add_argument(
        "--init", action="store_true", default=False, help="Create a new tasks.py file in the current directory"
    )
    _add_initial_tasks_to_parser(root_parser)
    root_parser.add_argument(
        "--examples", action="store_true", default=False, help="Show code examples of how to use taskcli."
    )
    root_parser.add_argument(
        ARG_NO_GO_TASK,
        action="store_true",
        default=False,
        help=(
            "Disable automatic inclusion of tasks from 'task' binary. "
            "Note, for the automaic inclusion to work, "
            f"{envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.name} must first be set."
        ),
    )
    root_parser.add_argument(
        "-P",
        "--print-return-value",
        action="store_true",
        default=False,
        help=(
            "advanced: print return value of task to stdout; useful when the task "
            "is a regular function which by itself does not print."
        ),
    )
    root_parser.add_argument(
        "-L",
        "--list-all",
        action="store_true",
        default=False,
        help="List everything, hidden tasks, hidden group, with max verbosity.",
    )
    root_parser.add_argument("--show-hidden", "-H", action="store_true", default=False)

    subparsers = root_parser.add_subparsers(help="Task to run")

    groups = []
    for task in tasks:
        # add group names

        group_name = task.group.name.replace(" ", "-").lower()
        if task.group not in groups:
            groups.append(task.group)
            subparser = subparsers.add_parser(group_name + GROUP_SUFFIX)
            subparser.set_defaults(task=group_name + GROUP_SUFFIX)

        # > groupandtask = "." + group_name + "." + task.name
        # > subparser = subparsers.add_parser(groupandtask)
        # > subparser.set_defaults(task=task.name)

        all_names_of_task = task.get_all_task_names()

        for name in all_names_of_task:
            subparser = subparsers.add_parser(name)
            subparser.set_defaults(task=name)

            if task.customize_parser:
                task.customize_parser(subparser)

            for param in task.params:
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
