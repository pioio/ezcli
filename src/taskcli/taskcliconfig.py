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
- tasks.py settings    -> taskcli.tt.config.show_hidden = True  (from ./tasks.py)
    runs during import, therefore already available in taskcli's main() function
    How to prevent imported modules from changing the defaults? taskcli.config.reset()
- env vars             -> run during dispatch
- CLI arguments        -> during dispatch

"""
import argparse
import logging
import os
from re import T
import typing
from typing import Any, Callable
from webbrowser import get

from . import constants, envvars, utils
from .envvar import EnvVar
from .logging import get_logger
from .types import UserError

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
        cli: bool = True,
        action: str = "",
        nargs: str = "",
        metavar: str = "",
        choices: list[str] | None = None,
        needed_early: bool = False,
    ):
        self.default = default
        self.name = name
        self.metavar = metavar or name.upper().replace("-", "_")
        self.short = short
        self.env = env
        self.desc = desc
        self.cli = cli  # whether to add to the CLI parser
        self.cli_arg_flag = "--" + name.replace("_", "-")
        self.env_var_name = env_var_name.upper() or "TASKCLI_CFG_" + name.upper()
        self.action = action
        self.nargs = nargs
        self.choices = choices
        self.needed_early = needed_early


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

        self.task: str = ""

        ## -------------------------------------------------------------------------------------------------------------
        # Accumulate functions used to configure the parser
        # need to come first, as they are used when creating other fields
        self._configure_parser: list[Callable[[argparse.ArgumentParser], None]] = []
        self._configure_early_parser: list[Callable[[argparse.ArgumentParser], None]] = []
        self._read_parsed_args: list[Callable[[TaskCLIConfig, argparse.Namespace], None]] = []
        self._read_from_env: list[Callable[[TaskCLIConfig], None]] = []
        self._addded_names: list[str] = list()
        self._addded_env_vars: list[EnvVar] = []

        ## -------------------------------------------------------------------------------------------------------------
        self.field_init: ConfigField = ConfigField(
            False,
            "init",
            env=False,
            desc="Create a new tasks.py file in the current directory",
        )
        self.init: bool = self._add_bool(self.field_init)


        ## -------------------------------------------------------------------------------------------------------------
        self.field_tags: ConfigField = ConfigField(
            [], "tags", "-t", nargs="+", desc="Only show tasks matching any of these tags"
        )
        self.tags: list[str] = self._add_list(self.field_tags)


        ## -------------------------------------------------------------------------------------------------------------
        # The order of groups of tasks when list
        # All tasks are by default in the "default" group unless task(group="foo") is used
        # Any group not listed here will be shown last, in the order they were defined.
        self.field_group_order: ConfigField = ConfigField(
            ["default"],
            "group_order",
            nargs="*",
            desc="Regex re.match patterns of the order in which top-level groups are shown. "
            "Any top-level group the name of which matches any of the patterns will be listed first.",
        )
        self.group_order: list[str] = self._add_list(self.field_group_order)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_search: ConfigField = ConfigField(
            "",
            "search",
            "-s",
            desc="Only show tasks whose name or description is matching this python regex seach pattern.",
        )
        self.search: str = self._add_str(self.field_search)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_parent = ConfigField(
            False,
            "parent",
            "-p",
            desc="Whether to also include tasks from the closest parent's directory's tasks.py",
            needed_early=True,
        )
        self.parent: bool = self._add_bool(self.field_parent)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_color = ConfigField(
            "",
            "color",
            choices=["auto", "always", "never"],
            env=False,
            desc=(
                "Whether or not the output should be colored"
            ),
        )
        self.color: str = self._add_str(self.field_color)

        ## -------------------------------------------------------------------------------------------------------------

        ## -------------------------------------------------------------------------------------------------------------
        default_show_hidden = False
        self.field_show_hidden: ConfigField = ConfigField(
            default_show_hidden,
            "show_hidden",
            constants.ARG_SHOW_HIDDEN_SHORT,
            desc="Show all tasks and groups, even the hidden ones.",
        )
        self.show_hidden: bool = self._add_bool(self.field_show_hidden)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_run_show_location: ConfigField = ConfigField(
            False,
            "run_show_location",
            desc="When true, each call to tt.run() also logs the code location from which it was called",
        )
        self.run_show_location: bool = self._add_bool(self.field_run_show_location)

        ## -------------------------------------------------------------------------------------------------------------
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

        ## -------------------------------------------------------------------------------------------------------------
        self.field_show_hidden_groups = ConfigField(
            False, "show_hidden_groups", desc="Listing will show groups that were marked with hidden=True"
        )
        self.show_hidden_groups: bool = self._add_bool(self.field_show_hidden_groups)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_show_hidden_tasks = ConfigField(
            False, "show_hidden_tasks", desc="Listing will show tasks that are marked with hidden=True"
        )
        self.show_hidden_tasks: bool = self._add_bool(self.field_show_hidden_tasks)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_show_tags = ConfigField(True, "show_tags", desc="Listing will show tags of each task.")
        self.show_tags: bool = self._add_bool(self.field_show_tags)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_show_optional_args = ConfigField(
            False, "show_optional_args", desc="Listing will show optional arguments of each task."
        )
        self.show_optional_args: bool = self._add_bool(self.field_show_optional_args)


        ## -------------------------------------------------------------------------------------------------------------
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
        ## -------------------------------------------------------------------------------------------------------------
        self.field_print_task_start_message = ConfigField(
            False,
            "print_task_start_message",
            desc=("Whether to print a log.info log message to stderr whenever a task starts."),
        )
        self.print_task_start_message: bool = self._add_bool(self.field_print_task_start_message)
        """Whether to print a log.info log message to stderr whenever a task starts."""

        ## -------------------------------------------------------------------------------------------------------------
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

        ## -------------------------------------------------------------------------------------------------------------
        self.field_hide_not_ready = ConfigField(
            False,
            "hide_not_ready",
            desc=(
                "Tasks which are not ready to run (e.g. due to missing env vars) "
                "will be automatically marked as hidden."
            ),
        )
        self.hide_not_ready: bool = self._add_bool(self.field_hide_not_ready)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_print_env = ConfigField(
            False, "print_env", action="store_true", env=False, desc="List the supported env vars"
        )
        self.print_env: bool = self._add_bool(self.field_print_env)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_print_env_detailed = ConfigField(
            False,
            "print_env_detailed",
            action="store_true",
            env=False,
            desc=f"Like {self.field_print_env.cli_arg_flag}, but also include descriptions.",
        )
        self.print_env_detailed: bool = self._add_bool(self.field_print_env_detailed)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_verbose = ConfigField(
            0, "verbose", "-v", action="count", desc="Verbose output, show debug level logs."
        )
        self.verbose: int = self._add_int(self.field_verbose)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_list = ConfigField(
            0, "list", "-l", action="count", env=False, desc="List tasks. Use -ll and -lll for a more detailed listing."
        )
        self.list: int = self._add_int(self.field_list)

        ## -------------------------------------------------------------------------------------------------------------
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

        ## -------------------------------------------------------------------------------------------------------------
        self.field_list_all = ConfigField(
            False,
            "list_all",
            "-L",
            desc=("Listing tasks shows all possible infomation. Extremely very verbose output."),
        )
        self.list_all: bool = self._add_bool(self.field_list_all)

        ## -------------------------------------------------------------------------------------------------------------
        self.default_options: list[str] = []
        self.default_options_tt: list[str] = []

        ## -------------------------------------------------------------------------------------------------------------
        self.field_print_debug = ConfigField(
            False,
            "print_debug",
            desc="Import the tasks and print detailed debug information. Use with, or without, specifying a task name.",
        )
        self.print_debug: bool = self._add_bool(self.field_print_debug)

        ## -------------------------------------------------------------------------------------------------------------
        self.field_file: ConfigField = ConfigField(
            # We should keep this one comma separated as otherwise it takes precedennce over the optional taskname.
            # But maybe there is a way to make argparse prefer to treat last argument as a tasknme.
            "",
            "file",
            "-f",
            needed_early=True,
            desc=(
                "Which taskfiles to use by default, you can specify multiple (comma separated), they will be merged."
                f"default is '{envvars.TASKCLI_TASKS_PY_FILENAMES.value}'"
            ),
        )
        self.file: str = self._add_str(self.field_file)

    def _store_name(self, name: str) -> None:
        """To prevent adding the same name twice."""
        assert name not in self._addded_names
        self._addded_names.append(name)

    #def __str__(self) -> str:

    def debug(self,fun:Callable[[Any],Any]|None=None) -> None:
        if fun is None:
            fun = print

        out = []
        for name in self._addded_names:
            field: ConfigField = getattr(self, "field_" + name)
            assert isinstance(field, ConfigField)
            envtxt = ""

            out += [f"{name}={getattr(self, name)}{envtxt}"]
        for out_ in out:
            fun(out_)

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
        if field.needed_early:
            self._configure_early_parser.append(add_argument)
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
        if field.needed_early:
            self._configure_early_parser.append(add_argument)
        if field.env:
            self._read_from_env.append(read_from_env)

        assert isinstance(field.default, str)
        return field.default

    def _add_list(self, field: ConfigField) -> list[str]:
        """Add a list of string to the parser."""
        assert field.nargs in ["*", "+", "?", ""], f"Invalid nargs: {field.nargs=}"
        args = self._shared_init_field(field)

        set_from = ""

        def add_argument(parser: argparse.ArgumentParser) -> None:
            help = field.desc
            help += f" (default: {field.default}{set_from})"
            parser.add_argument(*args, nargs=field.nargs, default=None, help=field.desc)

        def read_argument(config: TaskCLIConfig, args: argparse.Namespace) -> None:
            value = getattr(args, field.name)
            if value is not None:
                setattr(config, field.name, value)

        def read_from_env(config: TaskCLIConfig) -> None:
            env_var_name = self._to_env_var_name(field.name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(field.default), desc=field.desc, name=env_var_name)
                new_default_list = new_default.value.split(",")
                new_default_list = [x.strip() for x in new_default_list]
                setattr(config, field.name, new_default_list)

        if field.cli:
            self._configure_parser.append(add_argument)
            self._read_parsed_args.append(read_argument)
        if field.env:
            self._read_from_env.append(read_from_env)
        if field.needed_early:
            self._configure_early_parser.append(add_argument)

        assert isinstance(field.default, list), f"{field.name=} {field.default=}"
        return field.default

    def _add_int(  # noqa: C901
        self, field:ConfigField
    ) -> int:
        """Add a int to the parser."""
        args = self._shared_init_field(field)


        set_from = ""

        def add_argument(parser: argparse.ArgumentParser) -> None:
            help = ""
            help += f" (default: {field.default}{set_from})"
            if field.env:
                help += f" (env: {self._to_env_var_name(field.name)})"
            if field.action:
                parser.add_argument(*args, default=None, help=help, action=field.action)
            else:
                parser.add_argument(*args, default=None, help=help)

        def read_argument(config: TaskCLIConfig, args: argparse.Namespace) -> None:
            value = getattr(args, field.name)
            if value is not None:
                setattr(config, field.name, value)

        def read_from_env(config: TaskCLIConfig) -> None:
            env_var_name = self._to_env_var_name(field.name)
            if env_var_name in os.environ and os.environ[env_var_name] != "":
                new_default = EnvVar(default_value=str(field.default), desc=field.desc, name=env_var_name)
                try:
                    new_default_int = int(new_default.value)
                except ValueError as e:
                    msg = f"Could not convert '{new_default.value}' to int (env var {env_var_name})"
                    log.error(msg)
                    raise UserError(msg) from e
                setattr(config, field.name, new_default_int)

        # TODO if field.cli:
        self._configure_parser.append(add_argument)
        self._read_parsed_args.append(read_argument)
        if field.env:
            self._read_from_env.append(read_from_env)

        assert isinstance(field.default, int)
        return field.default

    def _to_env_var_name(self, name: str) -> str:
        return f"TASKCLI_CFG_{name.upper()}"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure the parser."""
        for f in self._configure_parser:
            f(parser)

    def configure_early_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure the early parser (used before dispatching)."""
        for f in self._configure_early_parser:
            f(parser)

    def read_parsed_arguments(self, args: argparse.Namespace) -> None:
        """Read the parsed arguments."""
        for f in self._read_parsed_args:
            f(self, args)

        if hasattr(args, "task"):
            self.task = args.task
        else:
            self.task = ""

    def read_env_vars_into_config(self) -> None:
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


runtime_config = TaskCLIConfig()  # modified with CLI arguments


_configs:dict[Any,TaskCLIConfig] = {}

def get_config() -> TaskCLIConfig:
    parent = utils.get_callers_module()
    if parent not in _configs:
        _configs[parent] = TaskCLIConfig()
    return _configs[parent]
