import logging

import inspect
log = logging.getLogger(__name__)

#from taskcli.taskcli import get_function_defaults

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


tasks = []


# def task(func):
#     tasks.append(func)
#     def wrapper():
#         log.debug("Before task decorator")
#         func()
#         log.debug("After decorator")

#     return wrapper

flavors = {}

# multi level decorator
def flavor(*args, **kwargs):
    def inner(func):
        flavors[func.__name__] = (args, kwargs)
        log.debug(f"Flavor decorator: {(args,kwargs)}")
        def wrapper():
            #log.debug("Before flavor decorator")
            func()
        return wrapper
    return inner

def task(*args, **kwargs):
    log.debug("Task decorator1")
    def inner(func):
        tasks.append(func)
        log.debug(f"Task decorator2: {(args,kwargs)}")
        if "flavors" in kwargs:
            flavors[func.__name__] = kwargs["flavors"]
        log.debug("")
        def wrapper():
            #log.debug("Before task decorator")
            func()
        return wrapper
    return inner

def somefunction():
    log.info("core - some function")


class Argument:
    def __init__(self, name, type, default=None):
        self.name = name
        self.type = type
        self.default = default



class Task:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.aliases = []

        self.description_short = ""
        self.description_long = ""
        docstring = inspect.getdoc(func)
        if docstring:
            self.description_short = docstring.splitlines()[0]
            self.description_long = docstring

        fspec = inspect.getfullargspec(func)
        log.debug(f"fspec: {fspec}")

        self.arguments = []
        default_argument_values:list = get_function_defaults(fspec)
        for i, arg in enumerate(fspec.args):
            default = default_argument_values[i]
            type = fspec.annotations.get(arg, None)

            # Infer type from the type of the default value, if present
            if not type and default is not None:
                if isinstance(default, bool):
                    type = bool
                elif isinstance(default, int):
                    type = int
                elif isinstance(default, float):
                    type = float
                elif isinstance(default, str):
                    type = str

            name = arg
            argument = Argument(name=name, type=type, default=default)
            self.arguments.append(argument)
