import argparse
import sys
from typing import Required

from .core import decorated_functions
from .core import extra_flavors
from .usage import get_usage_for_task

# from .core import tasks
from .core import (Task, Argument)
import logging

log = logging.getLogger(__name__)


def print_usage(tasks, help_level):
    print ("Usage:")
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



cli_config = {
    "setup_logging": False,
}

def setup_logging(conf, logging_format):
    cli_config["setup_logging"] = True

def do_setup_logging(verbosity):
    global cli_config
    if not cli_config["setup_logging"]:
        return

    level = logging.INFO
    if "-v" in sys.argv[1:]:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)7s: %(message)-50s     [%(filename)s:%(lineno)d]",
    )

from box import Box
class ArgumentError(Exception):
    pass


def is_flag(arg):
    return arg.startswith("-")


def print_arg_error(args, number):
    """ Number of "0" means first argument """
    count_chars_to_arg = 0

    for arg in args[:number]:
        count_chars_to_arg += len(arg) + 1
    print("------------------------------------------------------------------ ")

    arg0 = sys.argv[0]
    print("ERROR: " + arg0 + " " + " ".join(args))
    print("ERROR: " + ((len(arg0)+1)* "-") + "-" * count_chars_to_arg + "^" + "^" * (len(args[number]) - 1))

class ParsingContext:
    def __init__(self, tasks:list[Task]):
        self.arg_number = 0 # which argument are we parsing
        self.config = Box({})
        self.expect_value_for_arg:Argument|None = None
        self.active_task:Task|None = None
        self.active_task_cli_index = 0 # where on the CLi it was specified
        self.builtin_flags = {
            "-v": lambda x: self.config.update({"verbose": True}),
            "--verbose": lambda x: self.config.update({"verbose": True}),
            "-h": lambda x: self.config.update({"help": True}),
            "--help": lambda x: self.config.update({"help": True}),
        }
        self.tasks = tasks

        self.expect_next = ["builtin_flag", "task"]

        self._all_args = []

        self.parsed_tasks = []

    def expects(self, what):
        return what in self.expect_next

    def parse_args(self, args):
        self._all_args = args
        self.arg_number = 0 # so that we start with 1

        # Main parsing loop
        for arg in args:
            self.parse_arg(arg)

        if self.expect_value_for_arg:
            print_usage([self.active_task], 1)
            raise ArgumentError(f"Expected value for argument {self.expect_value_for_arg.name}, got nothing (ran out of arguments)")

        if self.active_task:
            self.finalize_parsing_of_task()

            self.parsed_tasks += [self.active_task]
            self.active_task = None

    def parse_arg(self, arg):
        self.arg_number += 1
        if is_flag(arg):
            self._parse_arg_flag(arg)
        else:
            self._parse_arg_not_flag(arg) # a task name, or

    def _parse_arg_flag(self, arg):
        assert is_flag(arg)
        if self.expect_value_for_arg:
            print_usage([self.active_task], 2)
            print_arg_error(self._all_args, self.arg_number - 1)
            raise ArgumentError(f"Expected value for {self.expect_value_for_arg.name}, got flag as argument {arg} number {self.arg_number}")

        if not self.active_task:
            if arg not in self.builtin_flags:
                print_usage([self.active_task], 2)
                print_arg_error(self._all_args, self.arg_number - 1)
                raise ArgumentError(f"Expected task, got flag as argument {arg} number {self.arg_number}")
            else:
                self.builtin_flags[arg](arg)
                return

        elif self.active_task:
            task_args = self.active_task.arguments
            found = False
            for targ in task_args:
                if arg == targ.short_cli_flag or arg == targ.long_cli_flag:
                    log.debug(f"Found flag {arg} ")
                    found = True
                    if targ.type == bool:
                        targ.value = True
                    else:
                        log.debug(f"Will expect value for {targ.name}")
                        self.expect_value_for_arg = targ
                    break
            if not found:
                print_usage([self.active_task], 2)
                print_arg_error(self._all_args, self.arg_number - 1)
                raise ArgumentError(f"Argument {arg} is not known for task {self.active_task.name_hyphenated}")

    def _parse_arg_not_flag(self, arg:str):
        assert not is_flag(arg)
        if self.expect_value_for_arg:
            log.debug(f"Found value for {self.expect_value_for_arg.name}: {arg}")
            assert_argument_type_matches(self.expect_value_for_arg, arg)

            self.expect_value_for_arg.value = arg
            self.expect_value_for_arg = None
            # TODO: add support for multiple value
            return
        else:
            task_names = [task.name for task in self.tasks]
            if arg not in task_names:
                print_usage([self.active_task], 1)
                print_arg_error(self._all_args, self.arg_number - 1)
                raise ArgumentError(f"Expected task name (one of {task_names}), but got '{arg}' as argument number {self.arg_number}")

            import copy
            if self.active_task:
                self.finalize_parsing_of_task()

            self.active_task = copy.deepcopy(self.tasks[task_names.index(arg)])
            self.active_task_cli_index = self.arg_number
            log.debug ("Active task: " + self.active_task.name)

    def finalize_parsing_of_task(self):
        assert self.active_task
        # if argument was not specified, but has default value, set it
        for arg in self.active_task.arguments:
            if arg.value is None and arg.default is not None:
                arg.value = arg.default

        # check if arguments are all set
        if missing_args  := self.active_task.get_missing_arguments():

            print_usage([self.active_task], 2)
            print_arg_error(self._all_args, self.active_task_cli_index - 1)
            raise ArgumentError(f"The following mandatory arguments were not specified for task {self.active_task.name_hyphenated}: {[x.name for x in missing_args]}")

        # finally, store the task for later execution
        self.parsed_tasks += [self.active_task]

def assert_argument_type_matches(arg:Argument, value):
    if arg.type == bool:
        if value not in ["True", "False"]:
            raise ArgumentError(f"Expected boolean value for {arg.name}, got '{value}'")
    if arg.type == int:
        if not value.isnumeric():
            raise ArgumentError(f"Expected integer value for {arg.name}, got '{value}'")
    if arg.type == str:
        if not isinstance(value, str):
            raise ArgumentError(f"Expected string value for {arg.name}, got '{value}'")
    if arg.type == float:
        try:
            float(value)
        except ValueError:
            raise ArgumentError(f"Expected float value for {arg.name}, got '{value}'")

log =  logging.getLogger(__name__)
def cli():
    """ Entry point for the CLI """

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)7s: %(message)-50s     [%(filename)s:%(lineno)d]",
    )


    args = sys.argv[1:]

    tasks = construct_tasks()
    if len(args) == 0:
        print_usage(tasks, 0)
        return

    expect_value = False
    expect_value_for = None

    ctx = ParsingContext(tasks)

    try:
        ctx.parse_args(args)
    except ArgumentError as e:
        print("ERROR: Argument error: " + str(e))
        print("ERROR: see above for details.")

    for task in ctx.parsed_tasks:
        conf = Box()
        conf.flavor_name = "default" # fixme
        run_task(task, conf)

    if expect_value:
        raise ArgumentError(f"Expected a value for argument {expect_value_for.name}, but arguments ended")



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
