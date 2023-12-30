"""The default runtime configuration of taskcli.

This file defines the default runtime configuration of taskcli which can be set via
- config file
- env vars
- CLI arguments

Note: some additional configurable env vars are in envvars.py.


Config load order
- built-in defaults    -> during import
- global config file   -> during import  (TODO)
- user config file     -> during import  (TODO)
- tasks.py settings    -> taskcli.config.show_hidden = True  (from ./tasks.py)
    How to prevent imported modules from changing the defaults? taskcli.config.reset()
- env vars             -> run during dispatch
- CLI arguments        -> during dispatch

"""
import argparse
import logging
import os
from typing import Any, Callable
import typing
from webbrowser import get

from . import constants, envvars, utils
from .envvar import EnvVar
from .task import UserError

from .logging import get_logger
log = get_logger(__name__)


if typing.TYPE_CHECKING:
    from .task import Task
class ConfigField:
    """A metadata field describing a configuration option.

    It's used internally to obtain e.g. env var name or cli args of fields.
    """

    def __init__(
        self,
        default: str | bool | int | list[str],
        name: str = "",
        short: str = "",
        /,
        *,
        desc: str = "",
        env: bool = True,
        env_var_name: str = "",
        cli:bool = True,
        action: str = "",
        nargs: str = "",
        metavar: str = "",
    ):
        self.default = default
        self.name = name
        self.metavar = metavar or name.upper().replace("-", "_")
        self.short = short
        self.env = env
        self.desc = desc
        self.cli = cli # whether to add to the CLI parser
        self.cli_arg_flag = "--" + name.replace("_", "-")
        self.env_var_name = env_var_name.upper() or "TASKCLI_CFG_" + name.upper()
        self.action = action
        self.nargs = nargs


class TaskCLIConfig:
    """The runtime configuration of taskcli.

    The object contains the baked-in default values for all configuration options.
    These default can later be overwritten from the env vars, or CLI arguments, or both.

    You can modify the runtime default values on per `tasks.py`-basis by setting e.g.
        form taskcli import tt
        tt.config.show_hidden = True

    The field prefixed with "field_" contain the metadata about each config option.
    This is used internally.

    Among other things, this object encapsulates the argparse logic.
    This in turn allows us to have good, typesafe, IDE integration (which native argparse.Namespace does not offer).

    The challenge this solves is the desire to have a single place which defines the
    - runtime configuration
    - config file options
    - env vars
    - CLI arguments
    Because, ideally, when adding a new switch we don't want to have to define it in 4 different places.
    """
    NO_CLI_FLAGS = "no-cli-flags"

    def __init__(self, load_from_env: bool = True):
        """Create a new TaskCLIConfig object.

        Arguments:
            load_from_env: If True, the config will be loaded from the environment variables.

        """
        self.load_from_env = load_from_env

        # Accumulate functions used to configure the parser
        self._configure_parser: list[Callable[[argparse.ArgumentParser], None]] = []
        self._read_parsed_args: list[Callable[[TaskCLIConfig, argparse.Namespace], None]] = []
        self._read_from_env: list[Callable[[TaskCLIConfig], None]] = []
        self._addded_names: set[str] = set()
        self._addded_env_vars: list[EnvVar] = []

        self.field_init: ConfigField = ConfigField(
            "", "init", env=False, desc="Create a new tasks.py file in the current directory"
        )
        self.init: str = self._add_str(self.field_init)

        self.tags: list[str] = self._add_list(
            [], "tags", "-t", nargs="+", help="Only show tasks matching any of these tags"
        )

        # The order of groups of tasks when list
        # All tasks are by default in the "default" group unless task(group="foo") is used
        # Any group not listed here will be shown last, in the order they were defined.

        self.group_order: list[str] =self._add_list(
            ["default"], "group_order", nargs="*",
            help="Regex re.match patterns of the order in which top-level groups are shown. "
                 "Any top-level group the name of which matches any of the patterns will be listed first."
                 )


        self.field_search: ConfigField = ConfigField(
            "",
            "search",
            "-s",
            desc="Only show tasks whose name or description is matching this python regex seach pattern.",
        )
        self.search: str = self._add_str(self.field_search)

        self.include_extra_tasks: bool = False
        self.extra_tasks_filter: Callable[["Task"], bool]|None = None

        self.field_extra_tasks_name_namespace = ConfigField(
            "p",
            "extra_tasks_name_namespace",
            cli=False,
            desc=("What task namespace to prefix to tasks when merging tasks from a upper directory level tasks.py. "
                  "See also: " + envvars.TASKCLI_EXTRA_TASKS_PY_FILENAMES.name
                  )
        )
        self.extra_tasks_name_namespace = self._add_str(self.field_extra_tasks_name_namespace)

        self.field_extra_tasks_alias_namespace = ConfigField(
            "",
            "extra_tasks_alias_namespace",
            cli=False,
            desc=(
                "What string to prefix to task aliases when merging tasks with a different tasks.py. "
                "See also: " + envvars.TASKCLI_EXTRA_TASKS_PY_FILENAMES.name
            )
        )
        self.extra_tasks_alias_namespace:str = self._add_str(self.field_extra_tasks_alias_namespace)

        default_show_hidden = False

        self.field_show_hidden: ConfigField = ConfigField(
            default_show_hidden,
            "show_hidden",
            constants.ARG_SHOW_HIDDEN_SHORT,
            desc="Show all tasks and groups, even the hidden ones.",
        )
        self.show_hidden: bool = self._add_bool(self.field_show_hidden)

        self.field_no_go_task = ConfigField(
            False,
            "no_go_task",
            desc=(
                "Disable automatic inclusion of tasks from 'task' binary. "
                "Note, for this automaic inclusion to work, "
                f"{envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.name} must first be set."
            ),
            action="store_true",
        )
        self.no_go_task: bool = self._add_bool(self.field_no_go_task)

        self.field_examples = ConfigField(False, "examples", desc="Print code examples of how to use taskcli.")
        self.examples: bool = self._add_bool(self.field_examples)

        self.field_show_hidden_groups = ConfigField(
            False, "show_hidden_groups", desc="Listing will show groups that were marked with hidden=True"
        )
        self.show_hidden_groups: bool = self._add_bool(self.field_show_hidden_groups)

        self.field_show_hidden_tasks = ConfigField(
            False, "show_hidden_tasks", desc="Listing will show tasks that are marked with hidden=True"
        )
        self.show_hidden_tasks: bool = self._add_bool(self.field_show_hidden_tasks)

        self.field_show_tags = ConfigField(True, "show_tags", desc="Listing will show tags of each task.")
        self.show_tags: bool = self._add_bool(self.field_show_tags)

        self.field_show_optional_args = ConfigField(
            False, "show_optional_args", desc="Listing will show optional arguments of each task."
        )
        self.show_optional_args: bool = self._add_bool(self.field_show_optional_args)

        self.field_show_default_values = ConfigField(
            False,
            "show_default_values",
            desc=(
                f"Listing will show default values of any arguments that are shown. "
                f"Use with {self.field_show_optional_args.cli_arg_flag} to also show values of "
                "the optional arguments."
            ),
        )
        self.show_default_values: bool = self._add_bool(self.field_show_default_values)

        self.field_show_ready_info = ConfigField(
            False,
            "show_ready_info",
            "-r",
            desc=(
                "Listing tasks will show detailed info about the task's readiness to be run. "
                "For example, it will list any required but missing environment variables. "
            ),
        )
        self.show_ready_info: bool = self._add_bool(self.field_show_ready_info)

        self.field_hide_not_ready = ConfigField(
            False,
            "hide_not_ready",
            desc=(
                "Tasks which are not ready to run (e.g. due to missing env vars) "
                "will be automatically marked as hidden."
            ),
        )
        self.hide_not_ready: bool = self._add_bool(self.field_hide_not_ready)

        self.field_print_env = ConfigField(False, "print_env", action="store_true", env=False, desc="List the supported env vars")
        self.print_env: bool = self._add_bool(self.field_print_env)

        self.field_print_env_detailed = ConfigField(
            False,
            "print_env_detailed",
            action="store_true",
            env=False,
            desc=f"Like {self.field_print_env.cli_arg_flag}, but also include descriptions.",
        )
        self.print_env_detailed: bool = self._add_bool(self.field_print_env_detailed)

        self.verbose: int = self._add_int(
            0, "verbose", "-v", action="count", help="Verbose output, show debug level logs."
        )

        self.list: int = self._add_int(
            0, "list", "-l", action="count", env=False, help="List tasks. Use -ll and -lll for a more detailed listing."
        )

        self.field_print_return_value = ConfigField(
            False,
            "print_return_value",
            "-P",
            desc=(
                "Advanced: print return value of the task function to stdout. Useful when the task "
                "is a regular function which by itself does not print, and only returns a value."
            ),
        )
        self.print_return_value: bool = self._add_bool(self.field_print_return_value)

        self.field_list_all = ConfigField(
            False,
            "list_all",
            "-L",
            desc=("Listing tasks shows all possible infomation. Extremely very verbose output."),
        )
        self.list_all: bool = self._add_bool(self.field_list_all)

        self.default_options: list[str] = []
        self.default_options_tt: list[str] = []

    def _store_name(self, name: str) -> None:
        """To prevent adding the same name twice."""
        assert name not in self._addded_names
        self._addded_names.add(name)

    def __str__(self) -> str:
        out = []
        for name in self._addded_names:
            field: ConfigField = getattr(self, "field_" + name)
            assert isinstance(field, ConfigField)
            envtxt = ""

            out += [f"{name}='{getattr(self, name)}'{envtxt}"]
        return "\n".join(out)

    def _store_env_var(self, name: str, default_value: str | bool | int | list[str], help: str) -> None:
        name = self._to_env_var_name(name)
        if isinstance(default_value, list):
            default_value = ",".join(default_value)
        if isinstance(default_value, bool):
            default_value = str(default_value).lower()
        if isinstance(default_value, int):
            default_value = str(default_value)
        ev = EnvVar(name=name, default_value=default_value, desc=help)
        self._addded_env_vars.append(ev)

    def get_env_vars(self) -> list[EnvVar]:
        """Return the list of all environment variables which are used to initialize the runtime configuration."""
        return self._addded_env_vars[:]

    def _get_args(self, name: str, short: str) -> list[str]:
        return ["--" + name.replace("_", "-")] + ([f"{short}"] if short else [])

    def _add_bool(self, field: ConfigField) -> bool:
        """Add a boolean flag to the parser."""
        args = self._shared_init_field(field)

        set_from = ""
        default = field.default

        def add_argument(parser: argparse.ArgumentParser) -> None:
            nonlocal field
            help = field.desc
            help += f" (default: {field.default}{set_from})"
            act: Any = "store_true" if not field.action else field.action
            # > act: Any = argparse.BooleanOptionalAction if not field.action else field.action
            parser.add_argument(*args, action=act, default=None, help=help)

        def read_argument(config: TaskCLIConfig, args: argparse.Namespace) -> None:
            value = getattr(args, field.name)
            if value is not None:
                setattr(config, field.name, value)

        def read_from_env(config: TaskCLIConfig) -> None:
            if field.env_var_name in os.environ:
                new_default = EnvVar(
                    default_value=str(field.default), desc=field.desc, name=field.env_var_name
                ).is_true()
                setattr(config, field.name, new_default)

        if field.cli:
            self._configure_parser.append(add_argument)
            self._read_parsed_args.append(read_argument)
        if field.env:
            self._read_from_env.append(read_from_env)

        assert isinstance(default, bool)
        return default

    def _shared_init_field(self, field: ConfigField) -> list[str]:
        self._store_name(field.name)
        if field.env:
            self._store_env_var(name=field.name, default_value=field.default, help=field.desc)
        args = self._get_args(field.name, field.short)
        return args

    def _add_str(self, field: ConfigField) -> str:
        """Add a str flag to the parser."""
        args = self._shared_init_field(field)

        def add_argument(parser: argparse.ArgumentParser) -> None:
            nonlocal field
            help = field.desc
            help += f" (default: {field.default})"
            parser.add_argument(
                *args, default=None, help=field.desc, type=str, nargs=None if not field.nargs else field.nargs
            )

        def read_argument(config: TaskCLIConfig, args: argparse.Namespace) -> None:
            value = getattr(args, field.name)
            if value is not None:
                setattr(config, field.name, value)

        def read_from_env(config: TaskCLIConfig) -> None:
            env_var_name = self._to_env_var_name(field.name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(field.default), desc=field.desc, name=env_var_name)
                setattr(config, field.name, new_default)

        if field.cli:
            self._configure_parser.append(add_argument)
            self._read_parsed_args.append(read_argument)
        if field.env:
            self._read_from_env.append(read_from_env)

        assert isinstance(field.default, str)
        return field.default

    def _add_list(
        self, default: list[str], name: str, short: str = "", /, *, nargs: str = "*", help: str, env: bool = True
    ) -> list[str]:
        """Add a list of string to the parser."""
        assert nargs in ["*", "+", "?", ""], f"Invalid nargs: {nargs}"
        self._store_name(name)
        if env:
            self._store_env_var(name=name, default_value=default, help=help)
        args = self._get_args(name, short)

        new_default = default
        set_from = ""

        def add_argument(parser: argparse.ArgumentParser) -> None:
            nonlocal help
            help += f" (default: {new_default}{set_from})"
            parser.add_argument(*args, nargs=nargs, default=None, help=help)

        def read_argument(config: TaskCLIConfig, args: argparse.Namespace) -> None:
            value = getattr(args, name)
            if value is not None:
                setattr(config, name, value)

        def read_from_env(config: TaskCLIConfig) -> None:
            env_var_name = self._to_env_var_name(name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(default), desc=help, name=env_var_name)
                new_default_list = new_default.value.split(",")
                new_default_list = [x.strip() for x in new_default_list]
                setattr(config, name, new_default_list)

        # TODO if field.cli:
        self._configure_parser.append(add_argument)
        self._read_parsed_args.append(read_argument)
        if env:
            self._read_from_env.append(read_from_env)

        return default

    def _add_int(  # noqa: C901
        self, default: int, name: str, short: str = "", /, *, help: str, action: str = "", env: bool = True
    ) -> int:
        """Add a list of string to the parser."""
        self._store_name(name)
        if env:
            self._store_env_var(name=name, default_value=default, help=help)
        args = self._get_args(name, short)

        new_default = default
        set_from = ""

        def add_argument(parser: argparse.ArgumentParser) -> None:
            nonlocal help
            help += f" (default: {new_default}{set_from})"
            if env:
                help += f" (env: {self._to_env_var_name(name)})"
            if action:
                parser.add_argument(*args, default=None, help=help, action=action)
            else:
                parser.add_argument(*args, default=None, help=help)

        def read_argument(config: TaskCLIConfig, args: argparse.Namespace) -> None:
            value = getattr(args, name)
            if value is not None:
                setattr(config, name, value)

        def read_from_env(config: TaskCLIConfig) -> None:
            env_var_name = self._to_env_var_name(name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(default), desc=help, name=env_var_name)
                try:
                    new_default_int = int(new_default.value)
                except ValueError as e:
                    msg = f"Could not convert {new_default.value} to int (env var {env_var_name})"
                    log.error(msg)
                    raise UserError(msg) from e
                setattr(config, name, new_default_int)

        # TODO if field.cli:
        self._configure_parser.append(add_argument)
        self._read_parsed_args.append(read_argument)
        if env:
            self._read_from_env.append(read_from_env)

        return default

    def _to_env_var_name(self, name: str) -> str:
        return f"TASKCLI_CFG_{name.upper()}"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure the parser."""
        for f in self._configure_parser:
            f(parser)

    def read_parsed_arguments(self, args: argparse.Namespace) -> None:
        """Read the parsed arguments."""
        for f in self._read_parsed_args:
            f(self, args)

    def read_from_env(self) -> None:
        """Read the parsed arguments."""
        for f in self._read_from_env:
            f(self)

    def get_fields(self) -> list[ConfigField]:
        """Return a list of all fields."""

        all_fields = []
        for field in self.__dict__.values():
            if isinstance(field, ConfigField):
                all_fields.append(field)
        return all_fields
        ##return [getattr(self, "field_" + name) for name in self._addded_names]

runtime_config = TaskCLIConfig()  # modified with CLI arguments
