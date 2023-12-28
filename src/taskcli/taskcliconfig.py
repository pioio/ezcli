"""
Config load order
- built-in defaults    -> during import
- global config file   -> during import
- user config file     -> during import
- tasks.py settings    -> taskcli.config.show_hidden = True  (from ./tasks.py)
    How to prevent imported modules from changing the defaults? taskcli.config.reset()
- env vars -> run during dispatch -> during dispatch
- CLI arguments                   -> during dispatch

"""
from typing import Any
import argparse
import os

from .task import UserError
from .envvar import EnvVar
from . import envvars
import logging
log = logging.getLogger(__name__)
class TaskCLIConfig:
    def __init__(self, load_from_env:bool = True):
        self.load_from_env = load_from_env

        # Accumulate functions used to configure the parser
        self._configure_parser = []
        self._read_parsed_args = []
        self._read_from_env = []
        self._addded_names = set()
        self._addded_env_vars:list[EnvVar] = []

        self.init:str = self._add_str("", "init", help="Create a new tasks.py file in the current directory")

        self.tags:list[str] = self._add_list([], "tags", "-t", help="Only show tasks matching any of these tags")

        self.show_hidden:bool = self._add_bool(False,
                                               "show_hidden",
                                               "-H",
                                               help="Show all tasks and groups, even the hidden ones."
                                               )

        #self.list:bool = self._add_bool(False, "list", help="")

        self.ARG_NO_GO_TASK = "--no-go-task"
        self.no_go_task:bool = self._add_bool(False, "no_go_task", help=(
            "Disable automatic inclusion of tasks from 'task' binary. "
            "Note, for this automaic inclusion to work, "
            f"{envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.name} must first be set.")
            ,
            action="store_true"
        )

        self.examples:bool = self._add_bool(False, "examples", help="Show code examples of how to use taskcli.")

        self.show_hidden_groups:bool = self._add_bool(False, "show_hidden_groups", help="")

        self.show_hidden_tasks:bool = self._add_bool(False, "show_hidden_tasks", help="")
        self.show_tags:bool = self._add_bool(False, "show_tags", "-T", help="Show tags of each task when listing tasks.")

        self.show_optional_args:bool = self._add_bool(False, "show_optional_args", help="")
        self.show_default_values:bool = self._add_bool(False, "show_default_values", help="")
        self.show_ready_info:bool = self._add_bool(
            False, "show_ready_info", "-r",
              help=("Listing tasks will show detailed info about the task's readiness to be run. "
                    "For example, it will list any required but missing environment variables. "))

        self.print_env:bool = self._add_bool(False, "print_env", action="store_true", help="List the supported env vars")
        self.print_env_detailed:bool = self._add_bool(False, "print_env_detailed", action="store_true", help="like --print-env, but also include descriptions.")

        self.verbose:int = self._add_int(0, "verbose", "-v", action="count",
                                         help="Verbose output, show debug level logs.")

        self.list:int = self._add_int(0, "list", "-l", action="count",
                                         help="List tasks. Use -ll and -lll for a more detailed listing.")

        self.print_return_value:bool = self._add_bool(False, "print_return_value", "-P", help=(
            "Advanced: print return value of the task function to stdout. Useful when the task "
            "is a regular function which by itself does not print, and only returns a value."
        ))

        self.list_all:bool = self._add_bool(
            False, "list_all", "-L",
              help="Listing tasks shows all possible infomation. Extremely very verbose output.")



    def _store_name (self, name:str) -> None:
        """To prevent adding the same name twice."""
        assert name not in self._addded_names
        self._addded_names.add(name)

    def _store_env_var(self, name, default_value:str|bool|int|list[str], help:str) -> None:
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
        return self._addded_env_vars[:]

    def _get_args(self, name, short) -> list[str]:
        return ["--" + name.replace('_', '-')] + ([f"{short}"] if short else [])

    def _add_bool(self,  default:bool, name:str, short:str="", /, *, help:str, action:str="") -> bool:
        """Add a boolean flag to the parser."""

        self._store_name(name)
        self._store_env_var(name=name, default_value=default, help=help)
        args = self._get_args(name, short)

        new_default = default
        set_from = ""

        def add_argument(parser):
            nonlocal help
            help += f" (default: {new_default}{set_from})"
            help += f" (env: {self._to_env_var_name(name)})"
            act:Any = argparse.BooleanOptionalAction if not action else action
            parser.add_argument(*args, action=act, default=None, help=help)

        def read_argument(config:TaskCLIConfig, args:argparse.Namespace):
            value =  getattr(args, name)
            if value is not None:
                setattr(config, name, value)

        def read_from_env(config:TaskCLIConfig):
            env_var_name = self._to_env_var_name(name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(default), desc=help, name=env_var_name).is_true()
                setattr(config, name, new_default)

        self._configure_parser.append(add_argument)
        self._read_parsed_args.append(read_argument)
        self._read_from_env.append(read_from_env)

        return default

    def _add_str(self, default:str, name:str, short:str="",  /, *, help:str) -> str:
        """Add a boolean flag to the parser."""
        self._store_name(name)
        self._store_env_var(name=name, default_value=default, help=help)
        args = self._get_args(name, short)

        new_default = default
        set_from = ""

        def add_argument(parser):
            nonlocal help
            help += f" (default: {new_default}{set_from})"
            help += f" (env: {self._to_env_var_name(name)})"
            parser.add_argument(*args, default=None, help=help)

        def read_argument(config:TaskCLIConfig, args:argparse.Namespace):
            value =  getattr(args, name)
            if value is not None:
                setattr(config, name, value)

        def read_from_env(config:TaskCLIConfig):
            env_var_name = self._to_env_var_name(name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(default), desc=help, name=env_var_name)
                setattr(config, name, new_default)

        self._configure_parser.append(add_argument)
        self._read_parsed_args.append(read_argument)
        self._read_from_env.append(read_from_env)

        return default

    def _add_list(self, default:list[str], name:str, short:str="",  /, *, help:str) -> list[str]:
        """Add a list of string to the parser."""
        self._store_name(name)
        self._store_env_var(name=name, default_value=default, help=help)
        args = self._get_args(name, short)

        new_default = default
        set_from = ""

        def add_argument(parser):
            nonlocal help
            help += f" (default: {new_default}{set_from})"
            help += f" (env: {self._to_env_var_name(name)})"
            parser.add_argument(*args, nargs="*", default=None, help=help)

        def read_argument(config:TaskCLIConfig, args:argparse.Namespace):
            value =  getattr(args, name)
            if value is not None:
                setattr(config, name, value)

        def read_from_env(config:TaskCLIConfig):
            env_var_name = self._to_env_var_name(name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(default), desc=help, name=env_var_name)
                new_default = new_default.value.split(",")
                new_default = [x.strip() for x in new_default]
                setattr(config, name, new_default)

        self._configure_parser.append(add_argument)
        self._read_parsed_args.append(read_argument)
        self._read_from_env.append(read_from_env)

        return default

    def _add_int(self, default:int, name:str, short:str="",  /, *, help:str, action:str="") -> int:
        """Add a list of string to the parser."""
        self._store_name(name)
        self._store_env_var(name=name, default_value=default, help=help)
        args = self._get_args(name, short)

        new_default = default
        set_from = ""

        def add_argument(parser):
            nonlocal help
            help += f" (default: {new_default}{set_from})"
            help += f" (env: {self._to_env_var_name(name)})"
            if action:
                parser.add_argument(*args, default=None, help=help, action=action)
            else:
                parser.add_argument(*args, default=None, help=help)


        def read_argument(config:TaskCLIConfig, args:argparse.Namespace):
            value =  getattr(args, name)
            if value is not None:
                setattr(config, name, value)

        def read_from_env(config:TaskCLIConfig):
            env_var_name = self._to_env_var_name(name)
            if env_var_name in os.environ:
                new_default = EnvVar(default_value=str(default), desc=help, name=env_var_name)
                try:
                    new_default = int(new_default.value)
                except ValueError as e:
                    msg = f"Could not convert {new_default.value} to int (env var {env_var_name})"
                    log.error(msg)
                    raise UserError(msg) from e
                setattr(config, name, new_default)

        self._configure_parser.append(add_argument)
        self._read_parsed_args.append(read_argument)
        self._read_from_env.append(read_from_env)

        return default

    def _to_env_var_name(self, name:str) -> str:
        return f"TASKCLI_CFG_{name.upper()}"

    def configure_parser(self, parser:argparse.ArgumentParser) -> None:
        """Configure the parser."""
        for f in self._configure_parser:
            f(parser)
    def read_parsed_arguments(self, args:argparse.Namespace) -> None:
        """Read the parsed arguments."""
        for f in self._read_parsed_args:
            f(self, args)
    def read_from_env(self) -> None:
        """Read the parsed arguments."""
        for f in self._read_from_env:
            f(self)

default_config = TaskCLIConfig() # built-in default config
runtime_config = TaskCLIConfig() # modified with CLI arguments