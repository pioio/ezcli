import dataclasses
import functools
import inspect
import os
import re
import sys

import argh  # type: ignore[import]

from . import configuration
from .configuration import config
from .decoratedfunction import DecoratedFunction
from .task import Task
from .types import Any, AnyFunction, Module

# ENDC = ""



def run(argv: list[str] | None = None, default:AnyFunction|None=None)->None:
    try:
        _run_unsafe(argv=argv, default=default)
    except Exception as _:
        if "_ARGCOMPLETE" in os.environ and "TASKCLI_LOG_COMPLETION_ERRORS" in os.environ:
            log_filename = "taskcli-completion-error.log"
            import logging
            logging.basicConfig(filename=log_filename, level=logging.DEBUG, format="%(asctime)s %(message)s")
            logging.exception("message")
        raise

def _run_unsafe(argv: list[str] | None = None, default:AnyFunction|None=None)->None:
    argv = argv or sys.argv[1:]
    calling_module = sys.modules[sys._getframe(2).f_globals["__name__"]]
    root_module = calling_module
    if "decorated_functions" not in calling_module.__dir__():
        # add decorated_functions to module
        calling_module.decorated_functions = [] # type: ignore[attr-defined]
    if not calling_module.decorated_functions:
        print("No tasks found, decorate a function with @task")
        sys.exit(1)




    # Decorate with module name
    def decorate_with_namespace(root_module:Module, functions:list[DecoratedFunction]) -> list[DecoratedFunction]:
        out = []
        for function in functions:
            func = function.func  # actual python function
            fun_module_name = sys.modules[func.__module__].__name__
            root_module_name = root_module.__name__
            if fun_module_name != root_module_name:
                new_name = fun_module_name + "." + func.__name__.replace("_", "-")
                func = argh.named(new_name)(func)
            function.func = func
            out.append(function)
        return out

    for fd in calling_module.decorated_functions:
        assert isinstance(fd, DecoratedFunction), f"Expected DecoratedFunction, got {type(fd)}"
    # functions = calling_module.decorated_functions
    functions = decorate_with_namespace(root_module, calling_module.decorated_functions)

    # module_of_function = calling_module.__name__

    # Detect if running in completion mode (e.g. after user pressed tab)
    # And if so, don't run the default command but instead forward execution
    # to argh, which will print the completion options
    if "_ARGCOMPLETE" in os.environ:
        # if completion dos not work, set _ARGCOMPLETE=1 and run task to see the error
        actual_functions = [func.func for func in functions]
        argh.dispatch_commands(actual_functions, argv=argv)
        sys.exit(0)

    if len(argv) == 0 and default:
        argh.dispatch_command(default, argv=argv)
    # TODO support '--list -vv'
    elif (
        (len(argv) == 0 and not default)
        or (argv and argv[0] == "--list")
        or (argv and argv[0] in ["-v", "-vv", "-vvv", "-vvvv", "-vvvv"])
    ):
        # print("No task specified! Listing tasks and their args ")
        verbose = config.render_default_list_details
        if "-v" in argv:
            verbose = 2
        elif "-vv" in argv:
            verbose = 3
        elif "-vvv" in argv:
            verbose = 4
        elif "-vvvv" in argv:
            verbose = 4
        elif "-vvvvv" in argv:
            verbose = 4
        if "-H" in argv:
            config.show_hidden_tasks = True

        _list_tasks(functions, root_module=root_module, verbose=verbose)
    else:
        actual_functions = [func.func for func in functions]
        argh.dispatch_commands(actual_functions, argv=argv)







def create_groups(tasks: list[Task], group_order: list[str]) -> dict[str, list[Task]]:
    """Return a dict of group_name -> list of tasks, ordered per group_order, group not listed there will be last."""
    groups:dict[str,list[Task]] = {}
    remaining_tasks = set()
    for expected_group in group_order:
        for task in tasks:
            assert isinstance(task.func, DecoratedFunction), f"Expected DecoratedFunction, got {type(task.func)}"
            if task.func.group.name == expected_group:
                if expected_group not in groups:
                    groups[expected_group] = []
                groups[expected_group].append(task)
            else:
                remaining_tasks.add(task)
    for task in remaining_tasks:
        if task.func.group.name not in groups:
            groups[task.func.group.name] = []
        groups[task.func.group.name].append(task)
    return groups

def strip_escape_codes(s:str) ->str :

    ENDC = configuration.get_end_color()
    UNDERLINE = configuration.get_underline()

    return re.sub(r"\033\[[0-9;]*m", "", s).replace(ENDC, "").replace(UNDERLINE, "")

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


def _list_tasks(decorated_functions: list[DecoratedFunction], root_module:Any, verbose:int) -> None:
    ENDC = configuration.get_end_color()

    tasks = []
    for func in decorated_functions:
        # TODO: does tno account for @argh.named
        name = func.func.__name__.replace("_", "-")
        assert isinstance(func, DecoratedFunction), f"Expected DecoratedFunction, got {type(func)}"
        task = Task(func=func, name=name)
        tasks.append(task)

    # TODO: extract groups info
    groups = create_groups(tasks=tasks, group_order=configuration.config.group_order)

    for task in tasks:
        module_name = task.func.__module__
        root_module_name = root_module.__name__
        prefix = ""
        if module_name != root_module_name:
            prefix = f"{module_name}."
        task.prefix = prefix


    # first, prepare rows, row can how more than one line
    rows:list[Row|SeparatorRow] = []

    for group_name, tasks in groups.items():
        if len(groups) > 1:
            rows.append(SeparatorRow(name=group_name))

        for task in tasks:
            row = Row(task)
            task_name = task.name
            task_name = f"{task_name.ljust(config.render_min_task_name)}"
            if task.func.important:
                format = SafeFormatDict(name=task_name, clear_format=configuration.colors.end)
                colors = {
                    color: value for color, value in configuration.colors.__dict__.items() if isinstance(value, str)
                }
                format.update(colors)
                task_name = config.render_format_of_important_tasks.format(**format)
                task_name = f"{configuration.colors.blue}{task_name}{ENDC}"

            if verbose == 0:
                # args = build_pretty_arg_string(task, include_optional=False, include_defaults=False)
                row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC}"
                row.right_col = task.get_summary_line()
            if verbose == 1:
                args = build_pretty_param_string(task, include_optional=False, include_defaults=False)
                row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC} {args}"
                row.right_col = task.get_summary_line()
            if verbose == 2:
                args = build_pretty_param_string(task, include_optional=True, include_defaults=False)
                row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC} {args}"
                row.right_col = task.get_summary_line()
            if verbose == 3:
                args = build_pretty_param_string(task, include_optional=True, include_defaults=True)
                row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC}"
                row.right_col = task.get_summary_line()
                if args:
                    row.extra_lines = [args]
            if verbose == 4:
                args_list = build_pretty_param_list(
                    task, include_optional=True, include_defaults=True, truncate_long=False
                )
                row.left_col = f"{config.render_prefix}{config.render_color_task_name}{task_name}{ENDC}"
                row.right_col = task.get_summary_line()
                for arg in args_list:
                    row.extra_lines += [arg]
            rows += [row]

    ## determine longest left col
    line_lens = [len(strip_escape_codes(row.left_col)) for row in rows if not isinstance(row, SeparatorRow)]
    longest_left_col = max(line_lens)
    print_rows(rows, longest_left_col)

def print_rows(rows:list[Row|SeparatorRow], longest_left_col:int) -> None:
    # Print everything
    for row in rows:
        if isinstance(row, SeparatorRow):
            print(render_separator_row(row.name))
            continue
        # Each row has a different num of invisible characters we need to account for
        num_invisible_chars = len(row.left_col) - len(strip_escape_codes(row.left_col))

        maximum_left_col_len = longest_left_col
        maximum_left_col_len = min(maximum_left_col_len, config.render_max_left_column_width)
        maximum_left_col_len = max(maximum_left_col_len, config.render_min_left_column_width)

        justify_width = maximum_left_col_len + num_invisible_chars
        # justify_width = (justify_width, config.render_min_left_column_width)

        line = f"{row.left_col.ljust(justify_width)} {row.right_col}"
        # line = strip_escape_codes(line)
        print(line)
        for line in row.extra_lines:
            print(config.render_extra_line_indent + line)



class SafeFormatDict(dict[str,str]):
    """Makes placeholders in a string optional,

    e.g. "Hello {name}" will be rendered as "Hello {name}" if name is not in the dict.
    """

    def __missing__(self, key:str) -> str:
        return "{" + key + "}"  # Return the key as is


def render_separator_row(name: str) -> str:
    line_char = config.adv_render_separator_line_char
    assert len(line_char) in [1, 0], f"Expected line_char to be a zero or a single character, got {line_char}"

    end = configuration.get_end_color()
    underline = configuration.get_underline()
    color = configuration.config.render_color_group_name

    template = config.adv_render_separator_line_title + "{clear_format}"

    format = SafeFormatDict(name=name, color=color, end=end, underline=underline, clear_format=end, line_char=line_char)
    colors = {color: value for color, value in configuration.colors.__dict__.items() if isinstance(value, str)}
    format.update(colors)

    line = template.format_map(format)

    # num_visible_chars = len(strip_escape_codes(line))

    # if configuration.config.render_group_header_len != -1:
    #     if num_visible_chars < configuration.config.render_group_header_len:
    #         line += line_char * (configuration.config.render_group_header_len - num_visible_chars)
    # else:
    #     import os
    #     if os.isatty(1):
    #         cols = os.get_terminal_size().columns
    #     else:
    #         cols = 40
    #     if num_visible_chars < cols:
    #         line += line_char * (cols - num_visible_chars)
    return line




def build_pretty_param_string(task: Task, include_optional:bool=True, include_defaults:bool=True, truncate_long:bool=True) -> str:
    ENDC = configuration.get_end_color()
    pretty_params = build_pretty_param_list(task, include_optional=include_optional, include_defaults=include_defaults)
    return f"{config.render_color_summary},{ENDC}".join(pretty_params)


def build_pretty_param_list(task: Task, include_optional:bool=True, include_defaults:bool=True, truncate_long:bool=True) -> list[str]:
    signature = inspect.signature(task.func.func)

    ENDC = configuration.get_end_color()

    pretty_params = []
    for param in signature.parameters.values():
        param_has_a_default = param.default is not inspect.Parameter.empty
        #    if not include_optional and param_has_a_default and (param.name not in config.render_always_show_args):
        if not include_optional and param_has_a_default:
            # skip args which have a default value specified
            continue
        if param_has_a_default and param.name in config.render_hide_optional_args:
            continue
        rendered = param.name

        if param.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
            rendered = param.name.upper()
        elif param.kind in [inspect.Parameter.KEYWORD_ONLY]:
            rendered = arg_to_cli_arg(param.name)
        elif param.kind in [inspect.Parameter.VAR_POSITIONAL]:
            rendered = f"*{param.name}"
        elif param.kind in [inspect.Parameter.VAR_KEYWORD]:
            rendered = f"**{param.name}"
        else:
            raise Exception(f"Unknown parameter kind: {param.kind}")

        if not param_has_a_default:
            rendered = f"{config.render_color_mandatory_arg}{rendered}{ENDC}"
        else:
            rendered = f"{config.render_color_optional_arg}{rendered}{ENDC}"

        if include_defaults and not param.annotation == bool:
            if param_has_a_default:
                # Shorten default value
                default_value = param.default
                if truncate_long:
                    if len(str(default_value)) > config.render_max_default_arg_width:
                        default_value = str(default_value)[: config.render_max_default_arg_width] + "..."

                rendered += (
                    f"{config.render_color_optional_arg}={ENDC}{config.render_color_default_arg}{default_value}{ENDC}"
                )
            else:
                rendered += ""
        pretty_params.append(rendered)

    return pretty_params


def arg_to_cli_arg(arg:str) -> str:
    """Convert foo_bar to --foo-bar, and g to -g"""
    if len(arg) == 1:
        return "-" + arg.replace("_", "-")
    else:
        return "--" + arg.replace("_", "-")


# def get_mandatory_and_optional_args(arg_spec: inspect.FullArgSpec):
#     """
#     Example:
#       args = ["a", "b", "c"]
#       defaults = ["2", "3"]
#       so, a is mandatory, b and c are optional
#       the defaultas ALWAYS apply from the end of the list
#     """
#     # they could be None, so cast to empty list
#     args = arg_spec.args or []
#     args_defaults = arg_spec.defaults or []

#     if len(args) != len(args_defaults):
#         num_mandatory_args = len(args) - len(args_defaults)
#         mandatory_args = args[:num_mandatory_args]
#         optional_args = args[num_mandatory_args:]
#     else:
#         mandatory_args = []
#         optional_args = args

#     return mandatory_args, optional_args




@dataclasses.dataclass
class Arg:
    name: str = ""
    default: Any = ""
    has_default: bool = False
    is_kwarg: bool = False


# def get_args(arg_spec) -> list[Arg]:
#     """Return a list of Arg objects, one for each argument of the function."""
#     out = []
#     mandatory_args, optional_args = get_mandatory_and_optional_args(arg_spec)
#     default_args = arg_spec.defaults or []

#     out.extend([Arg(name=arg, has_default=False, is_kwarg=False) for arg in mandatory_args])
#     out.extend(
#         [
#             Arg(name=arg, has_default=True, default=default, is_kwarg=False)
#             for arg, default in zip(optional_args, default_args)
#         ]
#     )

#     mandatory_kwargs, optional_args = get_mandatory_and_optional_kwargs(arg_spec)
#     default_kwargs = arg_spec.kwonlydefaults or {}

#     out.extend([Arg(name=arg, has_default=False, default=None, is_kwarg=True) for arg in mandatory_kwargs])
#     out.extend(
#         [Arg(name=arg, has_default=True, default=default, is_kwarg=True) for arg, default in default_kwargs.items()]
#     )

#     return out


# def get_mandatory_and_optional_kwargs(arg_spec:Any)-> :
#     # TODO: what is varkw?
#     args = arg_spec.kwonlyargs or []
#     defaults = arg_spec.kwonlydefaults or {}

#     mandatory_args = []
#     optional_args = []
#     for arg in args:
#         if arg in defaults:
#             optional_args.append(arg)
#         else:
#             mandatory_args.append(arg)
#     return mandatory_args, optional_args


# TODO: launch task from parent file





def include(module:Module, change_dir:bool=True, cwd:str="") -> None:
    """iterate over functions, functions with decorate @task should be"""
    import inspect
    import sys

    if "decorated_functions" not in module.__dir__():
        # add decorated_functions to module
        module.decorated_functions = [] # type: ignore[attr-defined]

    calling_module = sys.modules[inspect.stack()[1].frame.f_globals["__name__"]]

    if "decorated_functions" not in calling_module.__dir__():
        # add decorated_functions to module
        calling_module.decorated_functions = [] # type: ignore[attr-defined]

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
        assert isinstance(decorated_fun, DecoratedFunction), f"Expected DecoratedFunction, got {type(decorated_fun)}"
        # Decorate with CWD change
        if change_dir or cwd:
            if not cwd:

                module_which_defines_task_name = decorated_fun.func.__module__
                module_which_defines_task = sys.modules[module_which_defines_task_name]
                cwd = os.path.dirname(inspect.getfile(module_which_defines_task))
            decorated_fun.func = change_working_directory(decorated_fun.func, new_cwd=cwd)
        calling_module.decorated_functions.append(decorated_fun)
        # calling_module.decorated_functions.extend(module.decorated_functions)

    # calling_module.decorated_functions.extend(module.decorated_functions)



# def arg_optional(function, argument, *args, **kwargs):

#     if argument.replace("--", "") in inspect.signature(function).parameters:
#         # print(f"DECORATING {function.__name__} with {argument}")
#         function = argh.arg(argument, *args, **kwargs)(function)
#     return function
