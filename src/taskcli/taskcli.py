import argparse
import sys
from typing import Required

from .core import decorated_functions
from .core import extra_flavors
from .usage import get_usage_for_task

# from .core import tasks
from .core import Task
import logging

log = logging.getLogger(__name__)


def print_usage(tasks, help_level):
    lines = get_usage(tasks, help_level).splitlines()
    for line in lines:
        print(line)
    pass


def get_usage(tasks, help_level) -> str:
    lines = []
    for task in tasks:
        docstring = help_level > 1
        lines.extend(get_usage_for_task(task, docstring))
        lines.append("")
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
        p = argparse.ArgumentParser(add_help=False, usage="\n" + get_usage(tasks, 0))

        remaining_args = sys.argv[1:]
        if len(remaining_args) == 0:
            print_usage(tasks, 0)
            return

        # First, parse the default arguments
        p.add_argument("-v", "--verbose", action="count", default=0)
        p.add_argument("-h", "--help", action="count", default=0)
        p.add_argument(
            "task_name",
            help="Task to run",
        )
        p.add_argument(
            "flavor_name", help="Flavor to run", nargs="?", default="default"
        )
        conf, _ = p.parse_known_args(remaining_args)

        if conf.help:
            # p.print_help()
            print_usage(tasks, conf.help)
            if conf.help == 1:
                print("(for more detailed help use -hh)")
            return

        log.debug("parsing task and flavor name")

        conf, _ = p.parse_known_args(remaining_args)
        log.debug(f"parsed task_name: {conf.task_name}")
        # conf, remaining_arg = parse_arguments(p, remaining_args)
        task_name = conf.task_name
        task_names = [x.name_hyphenated for x in tasks]

        # Validate task exists
        if task_name not in task_names:
            p.print_help()
            print(f"Error: Task '{task_name}' not found.")
            print("Available tasks: " + ", ".join(task_names))
            sys.exit(1)

        # find task to run
        task_to_run = None
        for task in tasks:
            if task.name_hyphenated == conf.task_name:
                task_to_run = task
                break
        assert task_to_run is not None, "task_to_run should not be None"
        # validate flavor
        flavor_names = task_to_run.flavors.keys()
        if conf.flavor_name and conf.flavor_name not in flavor_names:
            p.print_help()
            print(f"Error: Task flavor '{conf.flavor_name}' not found.")
            print("Available flavors: " + ", ".join(flavor_names))
            sys.exit(1)

        assert task_to_run
        arg_names = [x.name for x in task_to_run.arguments]

        for arg in task_to_run.arguments:
            if not arg.short_cli_flag:
                p.add_argument(
                    arg.get_main_cli_flag(),
                    default=arg.default,
                    required=arg.default is None,
                )
            else:
                p.add_argument(
                    arg.get_main_cli_flag(),
                    arg.short_cli_flag,
                    default=arg.default,
                    required=arg.default is None,
                )

        # Parse again, this time for the task-specific arguments
        log.debug("last parse")
        try:
            conf = p.parse_args(sys.argv[1:])
        except SystemExit as e:
            # print_usage(tasks, conf.help)
            sys.exit(0)
        log.debug("Done last parse")

        for arg in arg_names:
            value = getattr(conf, arg)
            if not value:
                continue
            for arg2 in task_to_run.arguments:
                if arg2.name == arg:
                    arg2.value = value

                    # casting to type
                    if arg2.type == int:
                        arg2.value = int(value)
                    if arg2.type == bool:
                        arg2.value = bool(value)

                    break

    except argparse.ArgumentError as e:
        print("-------------------------------------------")
        print_usage(tasks, help_level=1)
        print("-------------------------------------------")
        print("Error: " + str(e))

        print("For correct usage see above.")
        sys.exit(1)

    log.debug(f"Tasks: {tasks}")

    run_task(task_to_run, conf)


def run_task(task, conf):
    log.debug(f"-------------- Running task {task.name_hyphenated}  -----------------")
    kwargs = task.get_kwargs(conf.flavor_name)
    log.debug("args:" + str(kwargs))
    task.func(**kwargs)
    log.debug("Finished running task")


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
