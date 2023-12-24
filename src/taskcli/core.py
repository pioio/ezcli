import dataclasses
import functools
import inspect
import os
import re
import sys
from random import choices
from token import NAME

from . import configuration, utils
from .configuration import config
from .decoratedfunction import Task
from .parser import dispatch
from .task import Task, task
from .taskcli import TaskCLI
from .types import Any, AnyFunction, Module
from .utils import param_to_cli_option

task_cli = TaskCLI()

def extra_args() -> str:
    """A string containing arguments passed to the script after "--".  See also extra_args_list()."""
    return " ".join(extra_args_list())

def extra_args_list() -> list[str]:
    """A list containing arguments passed to the script after "--".  See also extra_args()."""
    return task_cli.extra_args_list

def run(argv: list[str] | None = None, default:AnyFunction|None=None)->None:
    try:
        #_run_unsafe(argv=argv, default=default)
        dispatch(argv=argv)
    except Exception as _:
        if "_ARGCOMPLETE" in os.environ and "TASKCLI_LOG_COMPLETION_ERRORS" in os.environ:
            log_filename = "taskcli-completion-error.log"
            import logging
            logging.basicConfig(filename=log_filename, level=logging.DEBUG, format="%(asctime)s %(message)s")
            logging.exception("message")
        raise


def _extract_extra_args(argv:list[str], task_cli:TaskCLI) -> list[str]:
    first_double_hyphen = argv.index("--") if "--" in argv else -1
    if first_double_hyphen == -1:
        return argv
    else:
        task_cli.extra_args_list = argv[first_double_hyphen + 1 :]
        return argv[:first_double_hyphen]





@dataclasses.dataclass
class Row:
    task: Task
    left_col: str = ""
    right_col: str = ""
    extra_lines: list[str] = dataclasses.field(default_factory=list)
    is_separator = False

@dataclasses.dataclass
class SeparatorRow:
    name: str = ""




# def task_to_row(task:Task, verbose:int=1) -> Row:
#     ENDC = configuration.get_end_color()

#     row = Row(task)
#     task_name = task.name
#     task_name = f"{task_name.ljust(config.render_min_task_name)}"
#     if task.important:
#         format = SafeFormatDict(name=task_name, clear_format=configuration.colors.end)
#         colors = {
#             color: value for color, value in configuration.colors.__dict__.items() if isinstance(value, str)
#         }
#         format.update(colors)
#         task_name = config.render_format_of_important_tasks.format(**format)
#         task_name = f"{configuration.colors.blue}{task_name}{ENDC}"

#     if verbose == 0:
#         # args = build_pretty_arg_string(task, include_optional=False, include_defaults=False)
#         row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC}"
#         row.right_col = task.get_summary_line()
#     if verbose == 1:
#         args = build_pretty_param_string(task, include_optional=False, include_defaults=False)
#         row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC} {args}"
#         row.right_col = task.get_summary_line()
#     if verbose == 2:
#         args = build_pretty_param_string(task, include_optional=True, include_defaults=False)
#         row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC} {args}"
#         row.right_col = task.get_summary_line()
#     if verbose == 3:
#         args = build_pretty_param_string(task, include_optional=True, include_defaults=True)
#         row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC}"
#         row.right_col = task.get_summary_line()
#         if args:
#             row.extra_lines = [args]
#     if verbose == 4:
#         args_list = build_pretty_param_list(
#             task, include_optional=True, include_defaults=True, truncate_long=False
#         )
#         row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC}"
#         row.right_col = task.get_summary_line()
#         for arg in args_list:
#             row.extra_lines += [arg]

def render_rows(rows:list[Row|SeparatorRow], longest_left_col:int) -> list[str]:
    out = []
    # Print everything
    for row in rows:
        if isinstance(row, SeparatorRow):
            out += [render_separator_row(row.name)]
            continue
        # Each row has a different num of invisible characters we need to account for
        num_invisible_chars = len(row.left_col) - len(utils.strip_escape_codes(row.left_col))

        maximum_left_col_len = longest_left_col
        maximum_left_col_len = min(maximum_left_col_len, config.render_max_left_column_width)
        maximum_left_col_len = max(maximum_left_col_len, config.render_min_left_column_width)

        justify_width = maximum_left_col_len + num_invisible_chars
        # justify_width = (justify_width, config.render_min_left_column_width)

        line = f"{row.left_col.ljust(justify_width)} {row.right_col}"
        # line = strip_escape_codes(line)
        out += [line]
        for line in row.extra_lines:
            out += [config.render_extra_line_indent + line]
    out = [line.rstrip() for line in out]
    return out




# def render_separator_row(name: str) -> str:
#     line_char = config.adv_render_separator_line_char
#     assert len(line_char) in [1, 0], f"Expected line_char to be a zero or a single character, got {line_char}"

#     end = configuration.get_end_color()
#     underline = configuration.get_underline()
#     color = configuration.config.render_color_group_name

#     template = config.adv_render_separator_line_title + "{clear_format}"

#     format = SafeFormatDict(name=name, color=color, end=end, underline=underline, clear_format=end, line_char=line_char)
#     colors = {color: value for color, value in configuration.colors.__dict__.items() if isinstance(value, str)}
#     format.update(colors)

#     line = template.format_map(format)

#     # num_visible_chars = len(strip_escape_codes(line))

#     # if configuration.config.render_group_header_len != -1:
#     #     if num_visible_chars < configuration.config.render_group_header_len:
#     #         line += line_char * (configuration.config.render_group_header_len - num_visible_chars)
#     # else:
#     #     import os
#     #     if os.isatty(1):
#     #         cols = os.get_terminal_size().columns
#     #     else:
#     #         cols = 40
#     #     if num_visible_chars < cols:
#     #         line += line_char * (cols - num_visible_chars)
#     return line







def include(module:Module, change_dir:bool=True, cwd:str="") -> None:
    """iterate over functions, functions with decorate @task should be"""
    import inspect
    import sys

    import taskcli

    #decorated_functions = taskcli.get_runtime().tasks

    def change_working_directory(func:AnyFunction, new_cwd:str) -> Any:
        """change working directory to the directory of the module which defines the task, and then change back"""


        @functools.wraps(func)
        def wrapper(*args:Any, **kwargs:Any) -> Any:
            cwd = os.getcwd()
            os.chdir(new_cwd)
            try:
                return func(*args, **kwargs)
            finally:
                print("chaing back")
                os.chdir(cwd)

        return wrapper

    for decorated_fun in module.decorated_functions:
        assert isinstance(decorated_fun, Task), f"Expected DecoratedFunction, got {type(decorated_fun)}"
        # Decorate with CWD change
        if change_dir or cwd:
            if not cwd:

                module_which_defines_task_name = decorated_fun.func.__module__
                module_which_defines_task = sys.modules[module_which_defines_task_name]
                cwd = os.path.dirname(inspect.getfile(module_which_defines_task))
            decorated_fun.func = change_working_directory(decorated_fun.func, new_cwd=cwd)
        #calling_module.decorated_functions.append(decorated_fun)
        runtime = taskcli.get_runtime()
        runtime.tasks.append(decorated_fun)
        # calling_module.decorated_functions.extend(module.decorated_functions)

    # calling_module.decorated_functions.extend(module.decorated_functions)



