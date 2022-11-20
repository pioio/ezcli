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




def get_usage_line1(task):
    out = (
        "{color_task_name}{task_name:<20}"
        + bcolors.ENDC
        + "{color_description}{task_description}"
        + bcolors.ENDC
    )


    out = out.format(
        color_task_name=bcolors.OKGREEN ,
        task_name=task.name,
        color_description=bcolors.OKGREEN,
        task_description=task.description_short,
    )
    return out


def format_argument_line(flavor, flavors):
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

    longest_flavor_name = max(len(x.name) for x in flavors)
    size = str(longest_flavor_name)
    out = ("    {name:<" + size + "} {args}").format(name=name, args=all_args)
    return out

def get_usage_argument_lines(task):
    if not task.arguments:
        return []
    out = []

    for flavor_name, flavor in task.flavors.items():
        out.append("    " + task.name + " " + format_argument_line(flavor, task.flavors.values()))
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
