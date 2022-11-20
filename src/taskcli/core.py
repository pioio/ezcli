import logging

import inspect

log = logging.getLogger(__name__)

# from taskcli.taskcli import get_function_defaults


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


decorated_functions = []
# tasks = []

# def task(func):
#     tasks.append(func)
#     def wrapper():
#         log.debug("Before task decorator")
#         func()
#         log.debug("After decorator")

#     return wrapper
extra_flavors = {}
extra_aliases = {}

# multi level decorator
def flavor(*args, **kwargs):
    def inner(func):
        extra_flavors[func.__name__] = (args, kwargs)

        def wrapper():
            # log.debug("Before flavor decorator")
            func()

        return wrapper

    return inner


def task(*args, **kwargs):
    def inner(func):
        global decorated_functions
        decorated_functions.append(func)
        if "flavors" in kwargs:
            extra_flavors[func.__name__] = kwargs["flavors"]
        if "aliases" in kwargs:
            extra_aliases[func.__name__] = kwargs["aliases"]

        def wrapper():
            # log.debug("Before task decorator")
            func()

        return wrapper

    return inner


def somefunction():
    log.info("core - some function")


class Argument:
    def __init__(self, name, type, default=None, is_default=True):
        self.name = name
        self.type = type
        self.value = None
        self.default = default
        self.is_default = is_default

    def get_as_cli_flag(self):
        name = self.name.replace("_", "-")
        if len(name) == 1:
            return "-" + name
        else:
            return "--" + name


class Flavor:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments: list[Argument] = arguments


def get_argument_list(fspec):
    default_argument_values: list = get_function_defaults(fspec)
    out = []
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
        argument = Argument(name=name, type=type, default=default, is_default=True)
        out.append(argument)
    return out


class Task:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.name_hyphenated = self.name.replace("_", "-")
        self.aliases = []

        self.description_short = ""
        self.description_long = ""
        docstring = inspect.getdoc(func)
        if docstring:
            self.description_short = docstring.splitlines()[0]
            self.description_long = docstring

        fspec = inspect.getfullargspec(func)
        log.debug(f"fspec: {fspec}")

        self.flavors = {}

        self.arguments = []
        default_argument_values: list = get_function_defaults(fspec)
        self.arguments = get_argument_list(fspec)

        self.flavors["default"] = Flavor("default", self.arguments.copy())

        # Overlay extra flavors on top of default args
        # TODO: highlight differences in arguments with color
        # print(extra_flavors)
        for fun_name, eflav in extra_flavors.items():
            if fun_name != self.name:
                continue
            name, custom_arguments = eflav

            arguments_for_flav = get_argument_list(fspec)
            for arg in arguments_for_flav:
                if arg.name in custom_arguments:
                    arg.default = custom_arguments[arg.name]
                    # assert arg.type == type(arg.default), f"Type mismatch for argument {arg.name} in flavor {name}"
                    arg.is_default = False  # mark as customized

            flavor = Flavor(name, arguments_for_flav)
            self.flavors[name] = flavor

    def get_kwargs(self, flavor_name):
        assert flavor_name in self.flavors, f"Flavor {flavor_name} not found"

        out = {}
        for arg in self.flavors[flavor_name].arguments:
            out[arg.name] = arg.value
        return out
