import argparse
import sys
from typing import Required

from .core import decorated_functions
from .core import extra_flavors

# from .core import tasks
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
        color_task_name=bcolors.OKGREEN,
        task_name=task.name,
        color_description=bcolors.OKGREEN,
        task_description=task.description_short,
    )
    return out


offset_for_help = 20

def format_argument_line(flavor, flavors):
    # TODO: dynamically determine column width for each argument (will require considering all rows)
    args_str = "{value:<" + str(offset_for_help) +"}"

    arg_value_strings = []
    all_args = ""

    for arg in flavor.arguments:
        # align columns of arguments
        size = len(arg.name) + 5
        if arg.type == str:
            size = len(arg.name) + 15
        format = "{text:<" + str(size) + "} "

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
        out.append(
            "    "
            + task.name
            + " "
            + format_argument_line(flavor, task.flavors.values())
        )
    return out

def get_usage_docstring(task):
    docstring = inspect.getdoc(task.func)
    if not docstring:
        return []
    docstring = docstring.splitlines()[1:]
    out = docstring
    out = [" " * offset_for_help + bcolors.OKGREEN + x + bcolors.ENDC for x in out]
    return out


def print_usage(tasks, help_level):
    lines = get_usage(tasks, help_level).splitlines()
    for line in lines:
        print(line)
    pass

def get_usage(tasks, help_level):

    lines = []

    for task in tasks:
        lines.append(get_usage_line1(task))
        if help_level > 1:
            lines.extend(get_usage_docstring(task))
        lines.extend(get_usage_argument_lines(task))  # if any arguments present

    return "\n".join(lines)


def reset():
    extra_flavors.clear()


def construct_tasks():
    log.debug(f"Number of decorated functions: {len(decorated_functions)}")
    tasks = []
    for deco_fun in decorated_functions:
        task = Task(deco_fun)
        tasks.append(task)
    return tasks


def cli():
    """Testing"""

    log.debug(" ------------ cli - starting")
    tasks = construct_tasks()

    task_to_run = None
    try:

        p = argparse.ArgumentParser(add_help=False, usage="\n"+get_usage(tasks, 0))

        remaining_args = sys.argv[1:]
        if len(remaining_args) == 0:
            print_usage(tasks, 0)
            return

        # First, parse the default arguments
        p.add_argument("-v", "--verbose", action='count', default=0)
        p.add_argument("-h", "--help", action='count', default=0)
        p.add_argument("task_name", help="Task to run",)
        p.add_argument("flavor_name", help="Flavor to run", nargs="?", default="default")
        conf, _ = p.parse_known_args(remaining_args)


        if conf.help:
            #p.print_help()
            print_usage(tasks, conf.help)
            if conf.help == 1:
                print("(for more detailed help use -hh)")
            return

        log.debug("parsing task and flavor name")

        conf, _ = p.parse_known_args(remaining_args)
        log.debug(f"parsed task_name: {conf.task_name}")
        #conf, remaining_arg = parse_arguments(p, remaining_args)
        task_name = conf.task_name
        task_names = [x.name for x in tasks]

        # Validate task exists
        if task_name not in task_names:
            p.print_help()
            print(f"Error: Task '{task_name}' not found.")
            print("Available tasks: " + ", ".join(task_names) )
            sys.exit(1)

        # find task to run
        task_to_run = None
        for task in tasks:
            if task.name == conf.task_name:
                task_to_run = task
                break
        assert task_to_run is not None, "task_to_run should not be None"

        # validate flavor
        flavor_names = task_to_run.flavors.keys()
        if conf.flavor_name and conf.flavor_name not in flavor_names:
            p.print_help()
            print(f"Error: Task flavor '{conf.flavor_name}' not found.")
            print("Available flavors: " + ", ".join(flavor_names) )
            sys.exit(1)



        assert task_to_run

        # auto-determine short flags
        short_flags_used = ["v", "h"]
        arg_names = [x.name for x in task_to_run.arguments]
        for arg in task_to_run.arguments:
            short_flag = None
            long_flag = arg.get_as_cli_flag()
            if len(long_flag) >= 3: # is indeed long (a one-letter argument would return )
                first_letter = long_flag[2]
                first_letter_upper = first_letter.upper()
                if first_letter not in short_flags_used:
                    short_flags_used.append(first_letter)
                    short_flag = "-" + first_letter
                elif first_letter_upper not in short_flags_used:
                    short_flags_used.append(first_letter_upper)
                    short_flag = "-" + first_letter_upper
            else:
                short_flags_used += long_flag[1]

            if not short_flag:
                p.add_argument(
                    arg.get_as_cli_flag(),
                    default=arg.default,
                    required=arg.default is None)
            else:
                p.add_argument(
                    arg.get_as_cli_flag(),
                    short_flag,
                    default=arg.default,
                    required=arg.default is None)

        # Parse again, this time for the task-specific arguments
        log.debug("last parse")
        try:
            conf = p.parse_args(sys.argv[1:])
        except SystemExit as e:
            #print_usage(tasks, conf.help)
            sys.exit(0)
        log.debug("Done last parse")

        for arg in arg_names:
            value = getattr(conf, arg)
            if not value:
                continue
            for arg2 in task_to_run.arguments:
                if arg2.name == arg:
                    arg2.value = value
                    break

    except argparse.ArgumentError as e:
        print("-------------------------------------------")
        print_usage(tasks, help_level=1)
        print("-------------------------------------------")
        print("Error: " + str(e))

        print("For correct usage see above.")
        sys.exit(1)

    log.debug(f"Tasks: {tasks}")

    task = None
    for task in tasks:
        if task.name == task_name:
            task = task
            break

    run_task(task, conf)


def run_task(task, conf):
    log.debug("-------------- Running task -----------------")
    kwargs = task.get_kwargs(conf.flavor_name)
    log.debug("args:" + str(kwargs))
    task.func(**kwargs)

def parse_arguments(parser, remaining_args):
    log.debug("Parsing arguments")
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("-h", "--help", action="store_true", default=False)
    parser.add_argument("-H", "--full-help", action="store_true", default=False)

    parser.add_argument("task_name", help="Task to run")
    # parser.add_argument(
    #     "task_flavor_name", nargs="?", default="default", help="Task flavor to run"
    # )

    conf, remaining_args = parser.parse_known_args(remaining_args)
    log.debug(remaining_args)
    return conf, remaining_args


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
