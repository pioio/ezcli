import argparse

from .core import decorated_functions
from .core import extra_flavors
#from .core import tasks
from .core import Task
import logging

log = logging.getLogger(__name__)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def get_function_defaults(fspecs) -> list:
    args = fspecs
    defaults = []
    if args.defaults:
        num_missing_args = len(args.args) - len(args.defaults)
        for x in range(num_missing_args):
            defaults.append(None)
        defaults.extend(args.defaults)
    else:
        for x in range(len(args.args)):
            defaults.append(None)

    return defaults


import inspect


def format_argument_line(col1, col2):
    col1 = col1 + ":"
    return f"    {col1:<16}    {col2}"


def describe_task(func, full_docstring=False) -> list[str]:
    name = func.__name__
    """ decorator for describing tasks """
    # func = getattr(userconfig, name.replace("-", "_"))
    # log.debug("describe_task: ", func)
    fspec = inspect.getfullargspec(func)

    line1 = "* " + bcolors.OKGREEN + name.replace("_", "-") + bcolors.ENDC + " \t"
    docstring = inspect.getdoc(func)
    if docstring:
        first_doc_line = docstring.splitlines()[0]
        line1 += bcolors.UNDERLINE + first_doc_line + bcolors.ENDC

    config = func.__dict__.get("config", {})
    if "aliases" in config:
        line1 += f" (aliases: {', '.join(config['aliases'])})"

    line2 = ""
    all_arg_lines = []
    defaults = get_function_defaults(fspec)
    arg_string = ""

    column_width = 20

    if fspec.args:
        arg_string = ""

    default_arguments_str = []
    for i, arg in enumerate(fspec.args):
        if len(arg) == 1:
            arg_string += f"-{arg}"
        else:
            arg_string += f"--{arg.replace('_', '-')}"

        if defaults[i] is not None:
            arg_string += f"=" + str(defaults[i]) + ""
    if arg_string:
        arg_string = format_argument_line("defaults", arg_string)
        all_arg_lines.append(arg_string)
    # flavors
    flavor_lines = []
    for task_name, flavor in flavors.items():
        print(task_name, flavor)
        if task_name == name:
            name, args = flavor
            flavor_lines.append(format_argument_line(name, args))
    all_arg_lines.extend(flavor_lines)

    lines_of_args = []
    if all_arg_lines:
        # line2 += " ".join(args)
        for arg_line in all_arg_lines:
            lines_of_args.append(arg_line)

    out = [line1]
    out.extend(lines_of_args)

    # arg_lines =
    # if line2:
    #     out.append(line2)
    if docstring and full_docstring:
        docstring_lines = docstring.splitlines()
        docstring_lines = ["    " + line for line in docstring_lines]
        out.extend(docstring_lines)
    return out


def get_usage_line1(task):
    out = (
        "{color_task_name}{task_name:<20}"
        + bcolors.ENDC
        + "{color_description}{task_description}"
        + bcolors.ENDC
    )


    out = out.format(
        color_task_name=bcolors.OKGREEN,
        task_name=task.name,
        color_description=bcolors.UNDERLINE,
        task_description=task.description_short,
    )
    return out


def format_argument_line(flavor):
    # TODO: dynamically determine column width for each argument (will require considering all rows)
    args_str = "{value:<20}"

    arg_value_strings = []
    all_args = ""



    for arg in flavor.arguments:
        # align columns of arguments
        size = len(arg.name) + 5
        if arg.type == str:
            size = len(arg.name) + 15
        format = "{text:<"+str(size)+"} "

        single_arg_val = ""
        color = ""
        if not arg.is_default:
            color = bcolors.OKBLUE
        if arg.default is None:
            color = bcolors.FAIL

        single_arg_val += f"{arg.get_as_cli_flag()}"
        if arg.default:
            single_arg_val += f" {arg.default}"


        arg_value_strings.append(single_arg_val)
        all_args += color + format.format(text=single_arg_val) + bcolors.ENDC


    name = flavor.name
    if name == "default":
        name = "(default)"

    out = "    {name:<20} {args}".format(name=name, args=all_args)
    return out

def get_usage_argument_lines(task):
    if not task.arguments:
        return ["TASK HAS NO ARGUMENTS"]
    out = []

    for flavor_name, flavor in task.flavors.items():
        out.append(format_argument_line(flavor))
    return out


def print_usage(tasks):
    lines = []

    for task in tasks:
        log.debug(f"print_usage for {task.name}")
        lines.append(get_usage_line1(task))
        lines.extend(get_usage_argument_lines(task))  # if any arguments present

    for line in lines:
        print(line)
    pass


def cli():
    """Testing"""

    log.debug(" ------------ cli - starting")
    log.debug(f"num decorated functions: {len(decorated_functions)}")
    tasks = []
    for deco_fun in decorated_functions:
        task = Task(deco_fun)
        tasks.append(task)
    log.debug(f"Tasks: {tasks}")
    print_usage(tasks)


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Increase verbosity",
    )

    return parser
