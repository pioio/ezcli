import argparse
import inspect
import os
import sys
from json import load
from typing import Any, Iterable

import taskcli
import taskcli.core
from taskcli.task import UserError

from . import envvars, taskfiledev, utils
from .constants import GROUP_SUFFIX
from .envvar import EnvVar
from .group import get_all_groups_from_tasks
from .include import load_tasks_from_module_to_runtime
from .init import create_tasks_file
from .listing import list_tasks
from .logging import get_logger
from .parameter import Parameter
from .parser import build_parser, convert_types_from_str_to_function_type, extract_extra_args
from .task import Task
from .taskcli import TaskCLI
from .taskcliconfig import TaskCLIConfig
from .taskrendersettings import TaskRenderSettings
from .types import AnyFunction, Module
from .utils import param_to_cli_option, print_to_stderr

log = get_logger(__name__)


def dispatch(
    argv: list[str] | None = None,
    *,
    module: Module | None = None,
    sysexit_on_user_error: bool = True,
) -> Any:
    """Dispatch the command line arguments to the correct function.

    This function takes over once the `module` has imported/created all the tasks.

    In this wrapper function:
    - we load the Tasks from the `module` to the runtime context
    - we continue with the execution in the subsequent function

    TODO: break this apart into two functions, but unit tests would need a refactor, they use 'dispatch'.

    """
    # Initial parser, only used to find the tasks file
    log.debug("Dispatching with argv=%s", argv)
    if not argv:
        argv = _get_argv()

    if module is None:
        module = utils.get_callers_module()

    log.separator(f"Loading the included tasks (from {module.__name__} into the runetime ")
    log.trace(f"Module: {module=}, {id(module)=}")
    load_tasks_from_module_to_runtime(module)

    ###########################################################################################
    try:
        log.separator("Dispatching tasks.")
        return _dispatch(argv)
    except UserError as e:
        utils.print_error(f"{e}")
        if sysexit_on_user_error:
            sys.exit(1)
        else:
            # unit tests
            raise


########################################################################################################################
# Private functions


def _dispatch(argv: list[str] | None = None) -> Any:
    """Given the CLI args provided, decide what to do (e.g. list tasks or run a task)."""
    from taskcli.tt import config

    tasks: list[Task] = taskcli.core.get_runtime().tasks
    # only check for tasks later

    parser = build_parser(tasks)
    config.read_env_vars_into_config()
    config.configure_parser(parser)

    _do_argcomplete_and_exit(parser)

    argv = argv or sys.argv[1:]
    argv = extract_extra_args(argv, taskcli.core.get_runtime())

    log.debug(f"Parsing arguments: {argv}")
    argconfig = parser.parse_args(argv)
    config.read_parsed_arguments(argconfig)
    taskcli.core.get_runtime().parsed_args = argconfig

    # e.g. --init or --print-env actions
    if _run_subcommands_and_maybe_finish(config):
        return

    # This is the first place where we check if we actually found any tasks
    # in the files we opened. We can do this only after the parsing above
    _if_no_tasks_were_loaded_raise_sys_exit(tasks)

    _print_debug_info_tasks(config, tasks)

    # TODO
    # >  if argconfig.version:
    # >      print("version info...")
    # >      sys.exit(0)

    import taskcli.taskrendersettings as rendersettings

    render_settings = rendersettings.new_settings(config=config)

    if config.list or config.list_all:
        _print_list_tasks(tasks, render_settings=render_settings)
        return

    #####################################################################################
    # Lastly,
    if not config.task:
        # no 'task' argment was specified, so we list all loaded tasks
        _print_list_tasks(tasks, render_settings=render_settings)
        return None
    else:
        # User specified a task to run, or a group to list
        return _process_task_action(config, tasks, argconfig, render_settings)


def _process_task_action(
    config: TaskCLIConfig, tasks: list[Task], argconfig, render_settings: TaskRenderSettings
) -> Any:
    from .group import get_all_tasks_in_group

    if config.task.endswith(GROUP_SUFFIX):
        groups = get_all_groups_from_tasks(tasks)
        for group in groups:
            if group.get_name_for_cli() == argconfig.task[: -len(GROUP_SUFFIX)]:
                all_children_tasks: list[Task] = []
                get_all_tasks_in_group(group, all_children_tasks)
                utils.assert_no_dup_by_name(all_children_tasks)

                render_settings.show_hidden_groups = True
                render_settings.show_hidden_tasks = True
                _print_list_tasks(all_children_tasks, render_settings=render_settings)

        # should never happen
        sys.exit(9)
    else:
        for task in tasks:
            if task.name == argconfig.task:
                return _dispatch_task(task, argconfig)

        # Not found, search aliases
        for task in tasks:
            if argconfig.task in task.aliases:
                return _dispatch_task(task, argconfig)

        # task not found, fallback to search group name without a suffix
        groups = get_all_groups_from_tasks(tasks)
        for group in groups:
            if group.get_name_for_cli() == argconfig.task:
                all_children_tasks = []
                get_all_tasks_in_group(group, all_children_tasks)
                utils.assert_no_dup_by_name(all_children_tasks)
                render_settings.show_hidden_groups = True
                render_settings.show_hidden_tasks = True
                _print_list_tasks(all_children_tasks, render_settings=render_settings)
                sys.exit(1)

        print(f"Task {argconfig.task} not found")  # noqa: T201
        sys.exit(1)


def _dispatch_task(task: Task, argconfig) -> Any:
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
            value = convert_types_from_str_to_function_type(param, value)
            kwargs[name] = value
    if variable_args is not None:
        ret_value = task.func(*variable_args, **kwargs)
    else:
        ret_value = task.func(**kwargs)

    from taskcli import tt

    config = tt.config
    if config.print_return_value:
        print(ret_value)  # noqa: T201
    return ret_value


def _run_subcommands_and_maybe_finish(config: TaskCLIConfig) -> bool:
    """Return True if the called should exit."""
    if config.init is True:
        create_tasks_file()
        return True
    if config.print_env:
        envvars.show_env(verbose=False, extra_vars=config.get_env_vars())
        return True
    if config.print_env_detailed:
        envvars.show_env(verbose=True, extra_vars=config.get_env_vars())
        return True
    return False


def _if_no_tasks_were_loaded_raise_sys_exit(tasks: list[Task]) -> None:
    if not tasks:
        cwd = os.getcwd()
        msg = (f"taskcli: No files to include in '{cwd}'. Run 'taskcli --init' to create a new 'tasks.py', "
               "or specify one with -f .")
        print_to_stderr(msg, color="")
        sys.exit(1)


def _print_list_tasks(tasks: list[Task], render_settings: TaskRenderSettings) -> None:
    """Print the listed tasks."""
    lines = list_tasks(tasks, settings=render_settings)
    for line in lines:
        print(line)  # noqa: T201


def _print_debug_info_all_tasks():
    runtime = taskcli.core.get_runtime()
    for task in runtime.tasks:
        _print_debug_info_one_task(task)


def _print_debug_info_one_task(task: Task):
    fun = print
    fun(f"### Task: {task.name}")
    task.debug(fun)


def _print_debug_info_tasks(config: TaskCLIConfig, tasks: list[Task]):
    if config.print_debug is True:
        if not config.task:
            _print_debug_info_all_tasks()
        else:
            for task in tasks:
                if task.name == config.task:
                    _print_debug_info_one_task(task)
                    return
            utils.print_error(f"Task {config.task} not found")
        return


def _get_argv() -> list[str]:
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


def _do_argcomplete_and_exit(parser: argparse.ArgumentParser) -> None:
    magical_env = "_ARGCOMPLETE"
    if magical_env in os.environ:
        try:
            import argcomplete
        except ImportError:
            utils.print_error(
                f"`argcomplete` package not installed (but {magical_env=} is set), skipping tab completion"
            )
            return

        # NOTE: this it will immediately exit if it's a completion request,
        # no exception, no stack unwinding(!)
        argcomplete.autocomplete(parser)
