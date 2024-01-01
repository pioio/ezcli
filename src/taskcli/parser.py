import argparse
import inspect
import logging
import os
import sys
from ast import arg
from json import load
from re import U
from typing import Any, Iterable

import taskcli
import taskcli.core
from taskcli.task import UserError

from . import configuration, envvars, examples, taskfiledev, utils
from .constants import GROUP_SUFFIX
from .envvar import EnvVar
from .group import get_all_groups_from_tasks
from .include import load_tasks_from_module_to_runtime
from .init import create_tasks_file
from .listing import list_tasks
from .logging import get_logger
from .parameter import Parameter
from .task import Task
from .taskcli import TaskCLI
from .taskrendersettings import TaskRenderSettings
from .types import AnyFunction, Module
from .utils import param_to_cli_option, print_to_stderr, print_warning

""""
TODO:
  auto-aliases for commands

"""

log = get_logger(__name__)


def _extract_extra_args(argv: list[str], task_cli: TaskCLI) -> list[str]:
    first_double_hyphen = argv.index("--") if "--" in argv else -1
    if first_double_hyphen == -1:
        return argv
    else:
        task_cli.extra_args_list = argv[first_double_hyphen + 1 :]
        return argv[:first_double_hyphen]


def dispatch(
    argv: list[str] | None = None,
    *,
    module: Module | None = None,
    sysexit_on_user_error: bool = True,
) -> Any:
    """Dispatch the command line arguments to the correct function.

    This function takes over once `module` has imported/created all the tasks.

    In this wrapper function:
    - we load the Tasks from the `module` to the runtime context
    - we continue with the execution in the subsequent function

    TODO: break this apart into two functions, but unit tests would need a refactor, they use 'dispatch'.

    """
    # Initial parser, only used to find the tasks file
    log.debug("Dispatching with argv=%s", argv)
    if not argv:
        argv = get_argv()

    if module is None:
        module = utils.get_callers_module()

    log.separator(f"Loading the included tasks (from {module.__name__} into the runetime ")
    log.trace(f"Module: {module=}, {id(module)=}")
    load_tasks_from_module_to_runtime(module)

    try:
        log.separator("Dispatching tasks.")
        return _dispatch_unsafe(argv)
    except UserError as e:
        utils.print_error(f"{e}")
        if sysexit_on_user_error:
            sys.exit(1)
        else:
            # unit tests
            raise


def _dispatch_unsafe(argv: list[str] | None = None) -> Any:  # noqa: C901
    tasks: list[Task] = taskcli.core.get_runtime().tasks
    # only check for tasks later

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

    if config.verbose >= 2:
        count = 0
        for env in os.environ:
            if env.startswith("TASKCLI_"):
                print_to_stderr(f"{env}={os.environ[env]}")
                count += 1
        log.debug(f"Found {count} TASKCLI_ env vars")
    if config.init is True:
        create_tasks_file()
        return
    if config.print_env:
        envvars.show_env(verbose=False, extra_vars=config.get_env_vars())
        return
    if config.print_env_detailed:
        envvars.show_env(verbose=True, extra_vars=config.get_env_vars())
        return

    ########################################################################################
    # This is the first place where we check if we found any tasks
    from taskcli import tt

    if tt.get_runtime().tasks == []:
        cwd = os.getcwd()
        msg = f"taskcli: No files to include in '{cwd}'. Run 'taskcli --init' to create a new 'tasks.py', or specify one with -f ."
        print_to_stderr(msg, color="")
        sys.exit(1)

    ########################################################################################
    if config.print_debug is True:
        if not hasattr(argconfig, "task"):
            print_debug_info_all_tasks()
        else:
            for task in tasks:
                if task.name == argconfig.task:
                    print_debug_info_one_task(task)
                    return
            utils.print_error(f"Task {argconfig.task} not found")
        return

    # >  if argconfig.version:
    # >      print("version info...")
    # >      sys.exit(0)

    import taskcli.taskrendersettings as rendersettings

    render_settings = rendersettings.new_settings(config=config)

    if config.list or config.list_all:
        print_listed_tasks(tasks, render_settings=render_settings)
        return

    def _dispatch(task: Task) -> Any:
        kwargs = {}
        if not task.is_valid():
            # They should have been printed already during loading of the file
            msg = "Refusing to run task due to validation errors."
            raise UserError(msg)

        # convert parsed arguments to kwargs we can pass to the function
        variable_args = None
        for param in task.params:
            if not param.has_supported_type():
                log.debug(f"Not dispatching param {param.name} as it has unsupported type")
                continue
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

            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                variable_args = value
            else:
                value = _convert_types_from_str_to_function_type(param, value)
                kwargs[name] = value
        if variable_args is not None:
            ret_value = task.func(*variable_args, **kwargs)
        else:
            ret_value = task.func(**kwargs)
        if config.print_return_value:
            print(ret_value)  # noqa: T201
        return ret_value

    from .group import get_all_tasks_in_group

    if hasattr(argconfig, "task"):
        if argconfig.task.endswith(GROUP_SUFFIX):
            groups = get_all_groups_from_tasks(tasks)
            for group in groups:
                if group.get_name_for_cli() == argconfig.task[: -len(GROUP_SUFFIX)]:
                    all_children_tasks: list[Task] = []
                    get_all_tasks_in_group(group, all_children_tasks)
                    utils.assert_no_dup_by_name(all_children_tasks)

                    render_settings.show_hidden_groups = True
                    render_settings.show_hidden_tasks = True
                    print_listed_tasks(all_children_tasks, render_settings=render_settings)
                    # sys.exit(1)
            # should never happen
            sys.exit(9)
        else:
            for task in tasks:
                if task.name == argconfig.task:
                    return _dispatch(task)

            # Not found, search aliases
            for task in tasks:
                if argconfig.task in task.aliases:
                    return _dispatch(task)

            # task not found, fallback to search group name without a suffix
            groups = get_all_groups_from_tasks(tasks)
            for group in groups:
                if group.get_name_for_cli() == argconfig.task:
                    all_children_tasks = []
                    get_all_tasks_in_group(group, all_children_tasks)
                    utils.assert_no_dup_by_name(all_children_tasks)
                    render_settings.show_hidden_groups = True
                    render_settings.show_hidden_tasks = True
                    print_listed_tasks(all_children_tasks, render_settings=render_settings)
                    sys.exit(1)

            print(f"Task {argconfig.task} not found")  # noqa: T201
            sys.exit(1)
    else:
        print_listed_tasks(tasks, render_settings=render_settings)

    return None


def print_task_not_found_error(argv: list[str]) -> None:
    """Print the error message when no tasks are found."""
    # TODO, check upper dirs
    raise NotImplementedError("TODO")
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


# def _add_initial_tasks_to_parser(parser: argparse.ArgumentParser) -> None:
#     parser.add_argument(
#         "-f",
#         "--file",
#         required=False,
#         default="",
#         help=f"Which tasks file(s) to use, comma separate, first one found is used. default is '{DEFAULT_TASK_PY}'",
#     )
#     from taskcli import tt


# parser.add_argument( # TODO: deduplicate
#     tt.config.field_parent.short,
#     tt.config.field_parent.cli_arg_flag,
#     required=False,
#     default=tt.config.field_parent.default,
#     help = tt.config.field_parent.desc,
# )


def build_parser(tasks: list[Task]) -> argparse.ArgumentParser:  # noqa: C901
    """Build the parser."""
    log.trace("build_parser(): called for following tasks:")
    for task in tasks:
        log.trace(f"  {task}")

    root_parser = argparse.ArgumentParser()

    # _add_initial_tasks_to_parser(root_parser)

    subparsers = root_parser.add_subparsers(help="Task to run")

    groups = []
    added_subparsers = []
    for task in tasks:
        res = task.has_supported_type()
        if res != "ok":
            msg = f"Task {task.name} {task.code_location} has currently unsupported type: {res}"
            raise UserError(msg)

        # add group names
        from taskcli import Group

        # groups_visited: set[Group] = set()
        for group in task.groups:
            group_name = group.name.replace(" ", "-").lower()
            parser_name = group_name + GROUP_SUFFIX

            if parser_name in added_subparsers:
                # two groups with the same name, that's ok, ...
                continue

            if group not in groups:
                groups.append(group)

                subparser = subparsers.add_parser(parser_name)
                subparser.set_defaults(task=parser_name)
                added_subparsers += [parser_name]

        all_names_of_task = task.get_all_task_names()

        for name in all_names_of_task:
            try:
                subparser = subparsers.add_parser(name)
            except argparse.ArgumentError as e:
                reasons = ""
                if "conflicting subparser" in str(e):
                    reasons = (
                        " (conflicting subparser - try to rename the task, change its aliases, "
                        "or include it under a different namespace)"
                    )

                task_name = task.name
                import_location = ""
                if task.included_from:
                    import_location = f"Included from: {task.included_from.__file__}"

                utils.print_error(f"Failed to add command '{name}' (task: {task_name}). {reasons} {import_location}")
                sys.exit(1)
                continue
            subparser.set_defaults(task=name)
            added_subparsers += [name]

            if task.customize_parser:
                task.customize_parser(subparser)

            known_short_args: set[str] = set()
            for param in task.params:
                if not param.has_supported_type():
                    log.debug(f"Not adding {param.name} to parsers as it has unsupported type")
                    continue

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
        for group in task.groups:
            group_name = group.name.replace(" ", "-").lower()
            if group_name not in added_subparsers:
                subparser = subparsers.add_parser(group_name)
                subparser.set_defaults(task=group_name)
                added_subparsers += [group_name]

    return root_parser


def _add_param_to_subparser(args: list[str], param: Parameter, subparser: argparse.ArgumentParser) -> None:  # noqa: C901
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

    elif param.kind == inspect.Parameter.VAR_POSITIONAL:
        kwargs["nargs"] = "*"
        if param.has_default():
            kwargs["default"] = param.default

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

    log.trace(f"  subparser.add_argument: {args} {kwargs}")
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


def print_debug_info_all_tasks():
    runtime = taskcli.core.get_runtime()
    for task in runtime.tasks:
        print_debug_info_one_task(task)


def print_debug_info_one_task(task: Task):
    fun = print
    fun(f"### Task: {task.name}")
    task.debug(fun)


def get_argv() -> list[str]:
    """Return the command line arguments prefixed with default options if needed.

    There's a different set of default options for 't|taskcli' and 'tt' commands
    """
    from taskcli import tt

    if utils.is_basename_tt():
        # when calling with "tt"

        # Let's always add --show-hidden - more consistent behavior to users who forget to specify it
        # when customizing options.
        builtin_tt_options = ["--show-hidden"]
        argv = ["--show-hidden"] + tt.config.default_options_tt + sys.argv[1:]
        if tt.config.default_options_tt:
            log.debug(
                f"Using custom default options (tt): {tt.config.default_options_tt}, "
                f"plus the built-in options: {builtin_tt_options}"
            )
    else:
        # when calling with "t" or "taskcli"
        argv = tt.config.default_options + sys.argv[1:]
        if tt.config.default_options:
            log.debug(f"Using custom default options (taskcli): {tt.config.default_options}")
    return argv
