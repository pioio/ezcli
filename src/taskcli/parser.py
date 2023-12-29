import argparse
import inspect
import logging
import os
import sys
from ast import arg
from typing import Any, Iterable

import taskcli
import taskcli.core
from taskcli.task import UserError

from . import configuration, envvars, examples, taskfiledev, utils
from .constants import GROUP_SUFFIX
from .envvar import EnvVar
from .init import create_tasks_file
from .listing import list_tasks
from .parameter import Parameter
from .task import Task
from .taskcli import TaskCLI
from .taskrendersettings import TaskRenderSettings
from .types import AnyFunction
from .utils import param_to_cli_option

""""
TODO:
  auto-aliases for commands

"""


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


def dispatch(argv: list[str] | None = None, tasks_found: bool = True, sysexit_on_user_error: bool = True) -> Any:
    """Dispatch the command line arguments to the correct function."""
    # Initial parser, only used to find the tasks file
    log.debug("Dispatching with argv=%s", argv)
    try:
        return _dispatch_unsafe(argv, tasks_found)
    except UserError as e:
        utils.print_error(f"{e}")
        if sysexit_on_user_error:
            sys.exit(1)
        else:
            # unit tests
            raise


def _dispatch_unsafe(argv: list[str] | None = None, tasks_found: bool = True) -> Any:  # noqa: C901
    tasks: list[Task] = taskcli.core.get_runtime().tasks
    parser = build_parser(tasks)

    # Must happen before tab completion
    from taskcli.tt import config

    config.read_from_env()
    config.configure_parser(parser)

    if "_ARGCOMPLETE" in os.environ:
        import argcomplete

        print("Starting completion")  # for unit tests # noqa: T201
        argcomplete.autocomplete(parser)
        # it will exit if it's a completion request

    argv = argv or sys.argv[1:]

    argv = _extract_extra_args(argv, taskcli.core.get_runtime())

    log.debug(f"Parsing arguments: {argv}")
    argconfig = parser.parse_args(argv)

    config.read_parsed_arguments(argconfig)

    taskcli.core.get_runtime().parsed_args = argconfig

    if config.init:
        create_tasks_file("tasks.py")
        return
    if config.print_env:
        envvars.show_env(verbose=False, extra_vars=config.get_env_vars())
        return
    if config.print_env_detailed:
        envvars.show_env(verbose=True, extra_vars=config.get_env_vars())
        return

    # >  if argconfig.version:
    # >      print("version info...")
    # >      sys.exit(0)

    if not tasks_found:
        print_task_not_found_error(argv)
        sys.exit(1)

    import taskcli.taskrendersettings as rendersettings

    render_settings = rendersettings.new_settings(config=config)

    if config.list or config.list_all:
        print_listed_tasks(tasks, render_settings=render_settings)
        return
    if config.examples:
        examples.print_examples()
        return

    def _dispatch(task: Task) -> Any:
        kwargs = {}
        if not task.is_valid():
            # They should have been printed already during loading of the file
            msg = "Refusing to run task due to validation errors."
            raise UserError(msg)

        # convert parsed arguments to kwargs we can pass to the function
        for param in task.params:
            if not param.type.has_supported_type():
                # Skip it
                assert (
                    param.has_default()
                ), f"Param {param.name} does not have a default, dispatch should have never been called"
                continue
            name = param.name
            assert "-" not in param.name
            try:
                value = getattr(argconfig, name)
            except AttributeError:
                print(argconfig, sys.stderr)  # noqa: T201, debug
                raise

            value = _convert_types_from_str_to_function_type(param, value)
            kwargs[name] = value

        ret_value = task.func(**kwargs)
        if config.print_return_value:
            print(ret_value)  # noqa: T201
        return ret_value

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

            print_listed_tasks(tasks_in_group, render_settings=render_settings)
            sys.exit(1)
        else:
            for task in tasks:
                if task.get_full_task_name() == argconfig.task:
                    return _dispatch(task)

            # Not found, search aliases
            for task in tasks:
                if argconfig.task in task.aliases:
                    return _dispatch(task)

            # not found, search group name without a suffix
            groups = [task.group for task in tasks if task.group]
            groups = list(set(groups))
            for group in groups:
                if group.get_name_for_cli() == argconfig.task:
                    print_listed_tasks(group.tasks, render_settings=render_settings)
                    sys.exit(1)

            print(f"Task {argconfig.task} not found")  # noqa: T201
            sys.exit(1)
    else:
        print_listed_tasks(tasks, render_settings=render_settings)

    return None


def print_task_not_found_error(argv: list[str]) -> None:
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

    if taskfiledev.has_taskfile_dev() and not taskfiledev.should_include_taskfile_dev(argv):
        print(  # noqa: T201
            f"taskcli: Note: found a {local_taskfile} file. "
            "See the docs on how to include and list its tasks automatically."
        )
    sys.exit(1)


def filter_tasks_by_tags(tasks: list[Task], tags: Iterable[str]) -> list[Task]:
    """Filter tasks by tags."""
    if not tags:
        return tasks

    out = []
    for task in tasks:
        if task.tags:
            for tag in tags:
                if tag in task.tags:
                    out.append(task)
                    break
    return out


def print_listed_tasks(tasks: list[Task], render_settings: TaskRenderSettings) -> None:
    """Print the listed tasks."""
    lines = list_tasks(tasks, settings=render_settings)
    for line in lines:
        print(line)  # noqa: T201


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

    _add_initial_tasks_to_parser(root_parser)

    subparsers = root_parser.add_subparsers(help="Task to run")

    groups = []
    added_subparsers = []
    for task in tasks:
        # add group names

        group_name = task.group.name.replace(" ", "-").lower()
        if task.group not in groups:
            groups.append(task.group)
            subparser = subparsers.add_parser(group_name + GROUP_SUFFIX)
            subparser.set_defaults(task=group_name + GROUP_SUFFIX)
            added_subparsers += [group_name + GROUP_SUFFIX]

        # > groupandtask = "." + group_name + "." + task.name
        # > subparser = subparsers.add_parser(groupandtask)
        # > subparser.set_defaults(task=task.name)

        all_names_of_task = task.get_all_task_names()

        for name in all_names_of_task:
            subparser = subparsers.add_parser(name)
            subparser.set_defaults(task=name)
            added_subparsers += [name]

            if task.customize_parser:
                task.customize_parser(subparser)


            known_short_args = set()
            for param in task.params:
                args = param.get_argparse_names(known_short_args)
                if len(args) == 2:
                    # store the short flag for later, to prevent conflicts
                    assert len(args[1]) == 2, f"Expected short flag to be 2 chars, got {args[1]}"
                    known_short_args.add(args[1])
                _add_param_to_subparser(args=args, param=param, subparser=subparser)

    # finally, if 'group-name' is still available, add it as an aliast to "/"
    # if group-name and task-name have the same name, expecting here the task to take precedence
    # TODO: add unit test for this case
    for task in tasks:
        group_name = task.group.name.replace(" ", "-").lower()
        if group_name not in added_subparsers:
            subparser = subparsers.add_parser(group_name)
            subparser.set_defaults(task=group_name)
            added_subparsers += [group_name]

    return root_parser


def _add_param_to_subparser(args:list[str], param: Parameter, subparser: argparse.ArgumentParser) -> None:  # noqa: C901


    kwargs: dict[str, Any] = {}

    help_default = None

    if param.has_default():
        kwargs["default"] = param.default
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            kwargs["nargs"] = "?"

    if (
        param.arg_annotation
        and param.arg_annotation.type is not None
        and param.arg_annotation.type is not Parameter.Empty
    ):
        # user specified "arg(..., type=...)", which will be passed to argparse, which attempt the conversion
        # This check has to be first, as in principle we could be converting from str to str
        pass
    elif param.type.is_bool():
        kwargs["action"] = argparse.BooleanOptionalAction

        if param.has_default() and param.default in [True, False]:
            kwargs["default"] = param.default

        if not param.has_default() and not param.is_positional():
            kwargs["required"] = True

        if "nargs" in kwargs:
            del kwargs["nargs"]
        if "default" in kwargs:
            help_default = "true" if kwargs["default"] else "false"

    elif param.type.is_list():
        if param.has_default():
            kwargs["nargs"] = "*"  # it's ok for user to not pass it, default will be used
        else:
            kwargs["nargs"] = "+"  # User must pass it
            if not param.is_positional():
                # needed to force argparse to require --args, as by default they are optional
                kwargs["required"] = True

        if param.has_default():
            kwargs["default"] = param.default
    elif param.type.is_union_list_none():
        if param.has_default():
            kwargs["nargs"] = "*"
            kwargs["default"] = param.default
        else:
            kwargs["nargs"] = "+"
    elif param.type.raw in [int, float, str]:
        # to make argparse's internal type conversion work so that "choices=[111,222]" work
        kwargs["type"] = param.type.raw
    elif param.type.raw == taskcli.parametertype.ParameterType.Empty:
        pass

    else:
        # Assuming here that error will be printed when we try to run the task
        log.debug("Unsupported type %s, not adding to parser", param.type)
        return

    if param.help or help_default:
        kwargs["help"] = param.help
    if help_default:
        kwargs["help"] = "" if kwargs["help"] is None else kwargs["help"]
        kwargs["help"] += f" (default: {help_default})"

    # Finally, apply any custom argparse fields from the Arg annotation, but preserve the default value
    # because the Arg(default=foo) could have been set for the param, but could have later
    # been overridden in the function signature
    # This custom argparse fields should be applied only at the end
    if param.arg_annotation:
        kwargs = kwargs | param.arg_annotation.get_argparse_fields()

    subparser.add_argument(*args, **kwargs)


def _convert_types_from_str_to_function_type(param: Parameter, value: Any) -> Any:  # noqa: C901
    """Convert values from argparse to the types defined in the task."""
    if param.type.raw is int:
        value = int(value)
    elif param.type.is_bool():
        # TODO
        pass

    elif param.type.is_list():
        out = []
        thetype = param.type.get_list_type_args()
        for item in value:
            if thetype is not None:
                try:
                    out += [thetype(item)]
                except ValueError as e:
                    msg = f"Could not convert '{item}' to {thetype}"
                    raise UserError(msg) from e
            else:
                out += [item]
        value = out
    elif param.type.is_union_list_none():
        if value is None:
            return None

        # special case for test_list_int_or_none_default_none
        # the type is 'param:list[int]|None=None', when no params are specieid argpasrse offers []
        # But it makes sense to override this and return 'None' instead, as that's the default value specified
        # by the user
        if value == [] and param.has_default() and param.default is None:
            return None

        out = []
        thetype = param.type.get_list_type_args()
        for item in value:
            if thetype is not None:
                try:
                    out += [thetype(item)]
                except ValueError as e:
                    msg = f"Could not convert '{item}' to {thetype}"
                    raise UserError(msg) from e
            else:
                out += [item]
        value = out

        return value

    elif param.type.raw is float:
        value = float(value)

    # list of int
    # > elif param.type is list:
    # >     if hasattr(param.type, "__args__"):
    # >         if param.type.__args__[0] is int:
    # >             value = [int(x) for x in value]
    # >         else:
    # >             raise Exception(f"Type {param.type} not implemented")
    return value


def convert_elements_in_list_to_type(param: Parameter, value: Any) -> Any:
    """Convert elements in a list."""
    out = []
    thetype = param.type.get_list_type_args()
    for item in value:
        if thetype is not None:
            try:
                out += [thetype(item)]
            except ValueError as e:
                msg = f"Could not convert '{item}' to {thetype}"
                raise UserError(msg) from e
        else:
            out += [item]
    return out


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
