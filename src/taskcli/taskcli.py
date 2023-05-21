
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

num_tasks = 0
#task_data = {} # data from signatures

task_data = collections.defaultdict(dict) # data from signatures
task_data_args = collections.defaultdict(dict) # data from @arg decorators
task_data_params = collections.defaultdict(dict) # data from function signatures


def cleanup_for_tests():
    global num_tasks
    num_tasks = 0
    task_data_params.clear()
    task_data_args.clear()
    task_data.clear()



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
            print("mock_decorator")
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

    if param_default is not inspect._empty:
        # if default set, we want a option

        if len(param_name) == 1:
            ap_kwargs['param_names'] = [f"-{param_name}"]
        else:
            ap_kwargs['param_names'] = [f"--{param_name.replace('_', '-')}"]
            # TODO: add auto-adding short flags, but keep track which exist
    else:
        ap_kwargs['param_names'] = [param_name]
        # if no default set, we want a positional
        pass


    if param_type is not inspect._empty:
        ap_kwargs['type'] = param_type

        for list_type in [int,str,float,bool]:
            #print(",,,,,,,," + str(param_type), str(list[list_type]))
            if param_type == list[list_type]:
                ap_kwargs['nargs'] = '*'
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

    return ap_kwargs


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




    return ap_kwargs

EMPTY=inspect._empty

def trace(msg):
    print(msg)
    pass

def task(namespace=None, foo=None, env=None, required_env=None):
    """
    ns: command namespace. Allows for laying command in additional namespace
    env: environment variables to assert
    """
    #namespace = namespace
    global num_tasks
    num_tasks += 1

    def task_wrapper(fn):
        # this generated the decorator
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # this gets called right before the function
            func_name = fn.__name__

            # convert args and kwargs to a list of argpare args






            output = fn(*args, **kwargs)
            return output

        data = analyze_signature(fn)
        task_name = data['func_name']

        if task_name in task_data:
            raise Exception(f"Duplicate @task decorator on function '{task_name}' on line {inspect.getsourcelines(fn)[1]}")

        task_data[task_name] = data  # here we store all the raw data


        for param_data in data['params'].values():
            param_name = param_data['param_name']
            ap_kwargs = param_info_to_argparse_kwargs(param_data)

            # here, only the prepared argparse args
            task_data_params[task_name][param_name] = ap_kwargs

        return wrapper

    if callable(namespace):
        return task_wrapper(namespace) # return 'wrapper'
    else:
        return task_wrapper # ... or 'decorator'


def arg(*names, type=EMPTY, default=EMPTY, choices=None,required=EMPTY, help="", metavar=None,dest=None, nargs=None):
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
        main_name = names[0].lstrip('-').replace('-', '_')
        for name in names:
            if name in task_data_args[func_name]:
                raise Exception(f"Duplicate arg decorator for '{name}' in {func_name}")



        task_data_args[func_name][main_name] = arg_info_to_argparse_kwargs(func_sig_data)

        # check if matching param exists
        func_sig_data = analyze_signature(fn)
        task_name = func_sig_data['func_name']
        found = False
        for param in func_sig_data['params'].values():
            name = param['param_name']

            if name == main_name:
                found = True
        if not found:
            raise Exception(f"arg decorator for '{main_name}' in function '{func_name}' does not match any param in the function signature")


        print("decorating function", func_name, "with arg params:", func_sig_data )

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
    def error(self, message):
        # to make it more convenient to unit test
        self.print_help(sys.stderr)
        raise ParsingError(message)
        #self.exit(2, '%s: error: %s\n' % (self.prog, message))

def debug(*args, **kwargs):
    print("debug:", str(args), str(kwargs))

def build_parser(argv, exit_on_error=True):
    parser = ArgumentParser()

    assert len(argv) > 1, "No arguments provided"
    task_name = argv[1]

    if task_name not in task_data_params:
        print(f"Task {task_name} not found in {task_data_params.keys()}")
        # TODO support running with a default task
        sys.exit(111)

    for param_name in task_data_params[task_name].keys():

        DEFINED_VIA_ARG_DECORATOR = param_name in task_data_args[task_name]
        if DEFINED_VIA_ARG_DECORATOR:
            ap_kwargs = task_data_args[task_name][param_name]
            import copy
            copy_ap_kwargs = copy.deepcopy(ap_kwargs)

            # pop from a copy so that we can rerun cli() in unittest
            names = copy_ap_kwargs.pop('param_names')
            print(f"adding arg {param_name} from decoratorr {names} -- {ap_kwargs}")

            debug(*names, **ap_kwargs)
            parser.add_argument(
                *names,
                **copy_ap_kwargs,
            )
        else:
            ap_kwargs = task_data_params[task_name][param_name]
            import copy
            copy_ap_kwargs = copy.deepcopy(ap_kwargs)
            # pop from a copy so that we can rerun cli() in unittest
            names = copy_ap_kwargs.pop('param_names')
            print(f"adding arg {param_name} from signature {names} -- {ap_kwargs}")

            debug(*names, **ap_kwargs)
            parser.add_argument(
                *names,
                **copy_ap_kwargs,
            )

    return parser

def parse(parser,argv):
    print("## About to parse...")
    config = parser.parse_args(argv[2:])
    return config

def dispatch(config, task_name):
    print("## About to dispatch " + task_name)
    fun = task_data[task_name]['func']
    ret = fun(**vars(config))
    return ret

from typing import Any
def cli(argv=None, force=False) -> Any:
    if argv is None:
        argv = sys.argv

    # Detect if we're running as a script or not
    frame = inspect.currentframe()
    module = inspect.getmodule(frame.f_back)
    if (module.__name__ != "__main__") and not force:
        return

    print("## Prepping the parser")
    if len(argv) < 2:
        sys.exit("Error: No task name provided")
    task_name = argv[1]

    parser = build_parser(argv)
    config = parse(parser, argv)
    ret = dispatch(config, task_name)

    print("## Finished dispatch, returned", ret)

    print("done")
    return ret


