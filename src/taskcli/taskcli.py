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
task_data = {} # data from signatures
task_data_args = collections.defaultdict(dict) # data from @arg decorators

def cleanup_for_tests():
    global num_tasks
    num_tasks = 0
    task_data.clear()
    task_data_args.clear()



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
            output = fn(*args, **kwargs)
            return output

        data = analyze_signature(fn)
        func_name = data['func_name']
        task_data[func_name] = data
        trace(f"decorating function {func_name}")

        return wrapper

    if callable(namespace):
        return task_wrapper(namespace) # return 'wrapper'
    else:
        return task_wrapper # ... or 'decorator'

def arg(name, type, choices=None,required=False, help="", metavar=None,dest=None, nargs=None):
    # TODO some missing inthe signature
    def arg_decorator(fn):
        func_name = fn.__name__
        data = {
            'func_name': func_name,
            'name': name, # needs supporting multiple flags
            'type': type,
            'choices': choices,
            'required': required,
            'help': help,
            'metavar': metavar,
            'dest': dest,
            'nargs': nargs,
        }
        if name in task_data_args[func_name]:
            raise Exception(f"Duplicate arg decorator for '{name}' in {func_name}")

        task_data_args[func_name][name] = data
        print("decorating function", func_name, "with arg", name, data)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper

    return arg_decorator

class CustomArgumentParser(argparse.ArgumentParser):
    pass


def cli(argv=None, force=False) -> Any:
    if argv is None:
        argv = sys.argv

    # Detect if we're running as a script or not
    frame = inspect.currentframe()
    module = inspect.getmodule(frame.f_back)
    if (module.__name__ != "__main__") and not force:
        return

    print("## Dumping the parsed tasks")
    for task_name, task in task_data.items():
        print(task)

    print("## Prepping the parser")
    parser = argparse.ArgumentParser()

    assert len(argv) > 1, "No arguments provided"
    task_name = argv[1]

    if task_name not in task_data:
        print(f"Task {task_name} not found in {task_data.keys()}")
        # TODO support running with a default task
        sys.exit(111)

    for param_data in task_data[task_name]['params'].values():
        param_name = param_data['param_name']
        param_type = param_data['type']
        param_default = param_data['default']

        DEFINED_VIA_ARG_DECORATOR = param_name in task_data_args[task_name]
        if DEFINED_VIA_ARG_DECORATOR:

            print("adding arg from decoratore")
            arg_data = task_data_args[task_name][param_name]
            # TODO check if function signature does not set disallowed or conflicting elements

            kwargs = dict(
                type=arg_data['type'],
                choices=arg_data['choices'],
                #required=arg_data['required'],
                help=arg_data['help'],
                metavar=arg_data['metavar'],
#                dest=arg_data['dest'],
            )
            if arg_data['name'].startswith("--"):
                kwargs['required'] = arg_data['required']

            parser.add_argument(
                arg_data['name'],
                **kwargs
            )
        else:
            #raise Exception("Not implemented yet")
            if param_type is inspect._empty:
                print("adding arg 1")
                # TODO support default values
                parser.add_argument(param_name)
            else:
                print("adding arg 2", param_type, param_name)
                parser.add_argument(param_name, type=param_type)

    print("## About to parse..")
    try:
        config = parser.parse_args(argv[2:])
        print("## About to dispatch " + task_name)
        fun = task_data[task_name]['func']
        ret = fun(**vars(config))
        print("## Finished dispatch, returned", ret)

        pass
    except SystemExit:
        #log.exception("Failed to parse arguments")
        print("Failed to parse arguments")
        raise
    print("done")
    return ret


