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

log = get_logger(__name__)


def extract_extra_args(argv: list[str], task_cli: TaskCLI) -> list[str]:
    """Extract extra args (those after --) from argv list."""
    first_double_hyphen = argv.index("--") if "--" in argv else -1
    if first_double_hyphen == -1:
        return argv
    else:
        task_cli.extra_args_list = argv[first_double_hyphen + 1 :]
        return argv[:first_double_hyphen]


def build_parser(tasks: list[Task]) -> argparse.ArgumentParser:  # noqa: C901
    """Build the parser."""
    log.trace("build_parser(): called for following tasks:")
    for task in tasks:
        log.trace(f"  {task}")

    root_parser = argparse.ArgumentParser()

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


def convert_types_from_str_to_function_type(param: Parameter, value: Any) -> Any:  # noqa: C901
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


def _convert_elements_in_list_to_type(param: Parameter, value: Any) -> Any:
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
