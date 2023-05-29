
from collections.abc import Callable, Iterable, Sequence
from email.policy import default
import functools
from math import e
import os
import inspect
import argparse


import logging

import collections
log = logging.getLogger("taskcli")


#task_data = {} # data from signatures

class Task:
    def __init__(self) -> None:
        self.signature = {}  # raw signature data of the function/tasks
        self.data_args = {}  # data for argparse from @arg decorators
        self.data_params = {} # data for argparse parsed from the raw function signature (from parameters)
        self.required_env = None 
        self.is_main = False
        
        # To support decorators being in a different order, and throw errors if @task decorator is specified twice.
        self.task_decorator_seen = False

        # self.module_name = None

tasks = {}

# task_data = collections.defaultdict(dict) # data from @task decorators
# task_data_args = collections.defaultdict(dict) # data from @arg decorators
# task_data_params = collections.defaultdict(dict) # data from function signatures


def cleanup_for_tests():
    # called form unit test to cleanup global state between invocation.
    global tasks
    num_tasks = 0
    tasks = {}
    # task_data_params.clear()
    # task_data_args.clear()
    # task_data.clear()



# References:
#  - decorators in general
#    https://stackoverflow.com/questions/739654/how-do-i-make-function-decorators-and-chain-them-together
#  - decorators with optional parenthesis
#    https://stackoverflow.com/questions/35572663/using-python-decorator-with-or-without-parentheses

import sys

if sys.stderr.isatty() and sys.stdout.isatty():
    RED = '\033[91m'
    ENDC = '\033[0m'
else:
    RED = ''
    ENDC = ''

def mock_decorator():
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
        #    print("mock_decorator")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def analyze_signature(fn):
    # Get the signature of the decorated function
    signature = inspect.signature(fn)

    # Extract parameter names and types
    parameters = signature.parameters

    # function name
    func_name = fn.__name__

    # Store parameter information in the dictionary
    parameters = signature.parameters
    parameter_info = {}
    for name, param in parameters.items():
        typ = param.annotation
        default_value = param.default
        parameter_info[name] = {
            'type': typ,
            'default': default_value,
            'param_name': name,
        }

    data = {
        'func_name': func_name,
        "func": fn,
        "params": parameter_info,
        "module": fn.__module__
    }
    return data

def param_info_to_argparse_kwargs(param_data):
    param_name = param_data['param_name']
    param_type = param_data['type']
    param_default = param_data['default']

    ap_kwargs = {}
    #ap_kwargs['param_names'] = [param_data['param_name']]

    # if param_default is not inspect._empty:
    #     # if default set, we want a option

    # regardless off if we have a default or not, we want a option
    if len(param_name) == 1:
        ap_kwargs['param_names'] = [f"-{param_name}"]
    else:
        ap_kwargs['param_names'] = [f"--{param_name.replace('_', '-')}"]
    if param_default is inspect._empty:
        ap_kwargs['required'] = True

        # TODO: add auto-adding short flags, but keep track which exist
    # else:
    #     ap_kwargs['param_names'] = [param_name]
    #     # if no default set, we want a positional
    #     pass


    if param_type is not inspect._empty:
        ap_kwargs['type'] = param_type

        for list_type in [int,str,float,bool]:
            #print(",,,,,,,," + str(param_type), str(list[list_type]))
            if param_type == list[list_type]:
                if param_default is not inspect._empty:
                    raise Exception(f"Function params ({param_name}) of type 'list' must not have a default value. Use an @arg decorator instead.")
                ap_kwargs['nargs'] = '+'
                ap_kwargs['type'] = list_type

    if param_default is not inspect._empty:
        ap_kwargs['default'] = param_default

    if param_type is bool and param_default == False:
        ap_kwargs['action'] = 'store_true'
        ap_kwargs.pop('type') # otherwise argparse will complain

    if param_type is bool and param_default == True:
        ap_kwargs['action'] = 'store_false'
        ap_kwargs.pop('type') # otherwise argparse will complain

    if param_type is bool and param_default is inspect._empty:
        raise Exception("bool params must have a default value, otherwise they will be always true")

    if param_default is not inspect._empty:
        ap_kwargs['help'] = f"(default: {param_default})"

    #if param_default is inspect._empty:
    #    ap_kwargs['required'] = True

    # validations
    # print("aaaaaaaaaaaaaaaa")
    # print("validating", param_name, param_type, param_default)
    # if param_type == list and param_default is not inspect._empty:

    common_ap_kwargs_changes(ap_kwargs)
    return ap_kwargs


def common_ap_kwargs_changes(ap_kwargs):

    IS_POSITIONAL = ap_kwargs['param_names'][0] != '-'
    IS_REQUIRED = ap_kwargs.get('required', False)
    HAS_NOT_DEFAULT = 'default' not in ap_kwargs.keys()

    if (IS_POSITIONAL or IS_REQUIRED):

        if sys.stderr.isatty() and sys.stdout.isatty():
            RED = '\033[91m'
            ENDC = '\033[0m'
        else:
            RED = ''
            ENDC = ''

        if HAS_NOT_DEFAULT:
            help = ap_kwargs.get('help', '')
            ap_kwargs['help'] = f"{help} {RED}(required){ENDC}"
        else:
            ap_kwargs['help'] = f"(default: {ap_kwargs['default']})"


def arg_info_to_argparse_kwargs(arg_data):
    ap_kwargs = {}
    assert 'param_names' in arg_data, 'arg_data must have a name'
    ap_kwargs['param_names'] = arg_data['param_names']

    if arg_data.get('type', EMPTY) != EMPTY:
        ap_kwargs['type'] = arg_data['type']
    if arg_data.get('default', EMPTY) != EMPTY:
        ap_kwargs['default'] = arg_data['default']

    if arg_data.get('type') is not None:
        ap_kwargs['type'] = arg_data['type']
    if arg_data.get('choices') is not None:
        ap_kwargs['choices'] = arg_data['choices']
    if arg_data.get('help') is not None:
        ap_kwargs['help'] = arg_data['help']
    if arg_data.get('metavar') is not None:
        ap_kwargs['metavar'] = arg_data['metavar']
    if arg_data.get('nargs') is not None:
        ap_kwargs['nargs'] = arg_data['nargs']
    if arg_data.get('dest') is not None:
        ap_kwargs['dest'] = arg_data['dest']

    if arg_data.get('required', EMPTY) != EMPTY:
        ap_kwargs['required'] = arg_data['required']



    common_ap_kwargs_changes(ap_kwargs)
    return ap_kwargs

EMPTY=inspect._empty

def trace(msg):
    print(msg)
    pass

def task(namespace=None, foo=None, env=None, required_env=None, main=False):
    """
    ns: command namespace. Allows for laying command in additional namespace
    env: environment variables to assert
    main: if True, this task will be run if no task name is specified
    """


    def task_wrapper(fn):
        # this generats the decorator
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # this gets called right before the function
            func_name = fn.__name__

            required_envx = tasks[func_name].required_env
            if required_envx:
                # TODO: allow for * in env var name
                # TODO: allow for | in env var names
                # TODO: allow for global defaults
                missing = []
                empty = []
                for env in required_envx:
                    if env not in os.environ:
                        missing += [env]
                    elif os.environ[env] == "":
                        empty += [env]

                if missing or empty:
                    err = []
                    if missing:
                        err += [f"Missing required environment variables: {', '.join(missing)}"]
                    if empty:
                        err += [f"Empty required environment variables: {', '.join(empty)}"]
                    sys.exit("Error: " + ", ".join(err))

            output = fn(*args, **kwargs)
            return output


        func_signature = analyze_signature(fn)

        task_name = func_signature['func_name']
        if task_name in tasks and tasks[task_name].task_decorator_seen:
            raise Exception(f"Duplicate @task decorator on function '{task_name}' on line {inspect.getsourcelines(fn)[1]}")

        if task_name not in tasks:
            # could have been set by @arg decorator
            tasks[task_name] = Task()
        
        tasks[task_name].task_decorator_seen = True

        task = tasks[task_name]

        task.required_env = required_env
        task.is_main = main
        task.signature = func_signature
        
        if task.is_main:
            for other_tasks in [t for t in tasks.values() if t != task]:
                if other_tasks.is_main and main:
                    raise Exception(f"Multiple tasks marked as main. Only one @task decorator per namespace can be marked as main.")

        for param_data in task.signature['params'].values():
            param_name = param_data['param_name']
            ap_kwargs = param_info_to_argparse_kwargs(param_data)
            task.data_params[param_name] = ap_kwargs

        return wrapper

    # Needed, so that we can use "@task" and "@task()" interchangeably
    if callable(namespace):
        return task_wrapper(namespace) # return 'wrapper'
    else:
        return task_wrapper # ... or 'decorator'

# class VerifyDecorators:
#     def __init__(self):
#         self.current_task = None
#         self.previous_task = None

#     def processing_arg(self, func_name):
#         self.current_task = func_name
#         if self.previous_task != self.current_task:
#             for k,v in task_data.items():

import rich

def arg(*names, type=None, default=EMPTY, choices=None,required=EMPTY, help="", metavar=None,dest=None, nargs=None):
    # TODO some missing inthe signature
    def arg_decorator(fn):
        func_name = fn.__name__
        func_sig_data = {
            'func_name': func_name,
            'param_names': names, # needs supporting multiple flags
            'type': type,
            'choices': choices,
            'required': required,
            'help': help,
            'metavar': metavar,
            'dest': dest,
            'nargs': nargs,
        }
        
        if func_name not in tasks:
            tasks[func_name] = Task()


        primary_arg_name = names[0].lstrip('-').replace('-', '_')

        # assert no duplicates
        for name in names:
            if name in tasks[func_name].data_args:
                raise Exception(f"Duplicate arg decorator for '{name}' in {func_name}")

        tasks[func_name].data_args[primary_arg_name] = arg_info_to_argparse_kwargs(func_sig_data)


        # check if matching param exists
        func_sig_data = analyze_signature(fn)
        found = False
        for param in func_sig_data['params'].values():
            name = param['param_name']

            if name == primary_arg_name:
                found = True
        if not found:
            raise Exception(f"arg decorator for '{primary_arg_name}' in function '{func_name}' does not match any param in the function signature: ")


        #print("decorating function", func_name, "with arg params:", func_sig_data )

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper

    return arg_decorator

# class CustomArgumentParser(argparse.ArgumentParser):
#     pass

class ParsingError(Exception):
    pass
class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, print_help=True, **kwargs,):

        super().__init__(*args, **kwargs)
        self._print_help = print_help

    def error(self, message):
        # to make it more convenient to unit test
        self.print_help(sys.stderr)
        raise ParsingError(message)
        #self.exit(2, '%s: error: %s\n' % (self.prog, message))
    def print_help(self, *args, **kwargs):
        super().print_help(*args, **kwargs)
        #print("taskcli: error: the following arguments are required: -a")
        if hasattr(self, '_required_env') and self._required_env:
            # print to stderr
            print(f"", file=sys.stderr)
            print(f"environment variables:", file=sys.stderr)
            for env in self._required_env:
                if env not in os.environ:
                    print(f"  {env} {RED}(missing){ENDC}", file=sys.stderr)
                elif os.environ[env] == "":
                    print(f"  {env} {RED}(empty){ENDC}", file=sys.stderr)
                else:
                    print(f"  {env} ", file=sys.stderr)

    def set_env(self, required_env):
        self._required_env = required_env

def debug(*args, **kwargs):
    pass
    #print("debug:", str(args), str(kwargs))

def build_parser(argv, exit_on_error=True):
    parser = ArgumentParser()

    assert len(argv) > 1, "No arguments provided"
    task_name = argv[1].replace("-", "_")


    TASK_NAME_NOT_FOUND = task_name not in tasks
    OTHER_TASKS_ARE_DEFINED = len(tasks) > 0  # without this check, if there's no params at all, it would crash
    if TASK_NAME_NOT_FOUND and OTHER_TASKS_ARE_DEFINED:
        err = f"Task {task_name} not found among '{list(tasks.keys())}' tasks."
        # TODO support running with a default task
        raise Exception(err)
    if TASK_NAME_NOT_FOUND and not OTHER_TASKS_ARE_DEFINED:
        raise Exception("No tasks were defined. Use @task decorator to define tasks.")

    task = tasks[task_name]
    for param_name in task.data_params.keys():
        DEFINED_VIA_ARG_DECORATOR = param_name in task.data_args
        if DEFINED_VIA_ARG_DECORATOR:
            ap_kwargs = task.data_args[param_name]
            import copy
            copy_ap_kwargs = copy.deepcopy(ap_kwargs)

            # pop from a copy so that we can rerun cli() in unittest
            names = copy_ap_kwargs.pop('param_names')
            #print(f"adding arg {param_name} from decoratorr {names} -- {copy_ap_kwargs}")

            debug(*names, **copy_ap_kwargs)
            parser.add_argument(
                *names,
                **copy_ap_kwargs,
            )
        else:
            ap_kwargs = task.data_params[param_name]
            import copy
            copy_ap_kwargs = copy.deepcopy(ap_kwargs)
            # pop from a copy so that we can rerun cli() in unittest
            names = copy_ap_kwargs.pop('param_names')
            #print(f"adding arg {param_name} from signature {names} -- {copy_ap_kwargs}")

            debug(*names, **copy_ap_kwargs)
            parser.add_argument(
                *names,
                **copy_ap_kwargs,
            )

    return parser

def parse(parser,argv):
    #print("## About to parse...")
    config = parser.parse_args(argv[2:])
    return config

def dispatch(config, task_name):
    #print("## About to dispatch " + task_name)
    fun = tasks[task_name].signature["func"]
    ret = fun(**vars(config))
    # resolve reference to original function to its decorated variant
    # this way decorators trigger when we call it
    # module_name = task_data[task_name]['module']
    # module = sys.modules[module_name]
    # decorated_function = getattr(module, fun.__name__)
#
#decorated function
#
#
    # ret = decorated_function(**vars(config))
    return ret

# def assert_no_name_conflicts():
#     main_task_data = [k for k,v in tasks.items() if v['is_main']]
#     if not main_task_data:
#         return
#     MAIN_TASK_DEFINED = bool(main_task_data)

#     MAIN_TASK_HAS_POSITIONAL_ARGUMENTS = None
#     for arg in task_data_args[main_task_data[0]].values():
#         if arg['param_names'][0] != '-':
#             MAIN_TASK_HAS_POSITIONAL_ARGUMENTS = True
#             break
    


from typing import Any
def cli(argv=None, force=False) -> Any:
    if argv is None:
        argv = sys.argv

    # Detect if we're running as a script or not
    frame = inspect.currentframe()
    assert frame is not None
    module = inspect.getmodule(frame.f_back)
    assert module is not None
    if (module.__name__ != "__main__") and not force:
        return

    if len(argv) < 2:
        raise Exception("NOT IMPLEMENTED - defautl tasks")
        sys.exit("Error: No task name provided")
    task_name = argv[1].replace("-", "_")

    parser = build_parser(argv)
    # add env data
    import rich
    if task_name not in tasks or tasks[task_name].task_decorator_seen == False:
        raise Exception(f"Task {task_name} is not among known tasks. Did you forget to add the @task decorator?")

    task = tasks[task_name]
    if task.required_env:
        parser.set_env(task.required_env)

    config = parse(parser, argv)
    ret = dispatch(config, task_name)

    return ret


