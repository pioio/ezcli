# Funtions for printing usage information


from .core import Task, Flavor, Argument


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


# TODO: remove colors from taskcli
# TODO: add color support

indent_level_1 = 4
indent_level_2 = 8


def get_usage_for_tasks(tasks: list[Task], **kwargs) -> list[str]:
    lines: list[str] = []
    for task in tasks:
        lines.extend(get_usage_for_task(task, **kwargs))
    return lines


def get_usage_arguments(task: Task) -> list[str]:
    lines: list[str] = []
    for arg in task.arguments:
        line = f"{arg.name}"
        if arg.default is not None:
            line += f"={arg.default}"
        if arg.type is not None:
            line += f":{arg.type}"
        lines.append(line)
    return lines


def get_flags_for_argument(arg) -> str:
    long = arg.long_cli_flag
    short = arg.short_cli_flag
    assert short or long, "Argument must have a long or short flag"

    if long and short:
        return f"{short}|{long}"
    elif long:
        return long
    elif short:
        return short
    else:
        raise Exception(
            "Argument has neither long nor short flag, this should never happen"
        )


def get_line_for_argument(arg) -> str:
    arg_flags_format = "{lbracket}{flags}{rbracket}"
    if arg.default is not None:
        lbracket = "["
        rbracket = "]"
    else:
        lbracket = " "
        rbracket = " "

    flags = get_flags_for_argument(arg)
    arg_flags = arg_flags_format.format(
        lbracket=lbracket, flags=flags, rbracket=rbracket
    )

    arg_line_format = "{arg_flags:<20} {text}"

    text = ""
    if arg.default is not None:
        text = f"Default: {arg.default}"

    arg_line = arg_line_format.format(arg_flags=arg_flags, text=text)

    return arg_line


def get_line_for_flavor(flavor: Flavor) -> str:
    return flavor.name


def get_line_task_name(task: Task) -> str:
    return "{name:<20} {desc}".format(
        name=task.name_hyphenated, desc=task.description_short
    )


def get_usage_for_task(task: Task, print_doctring=False) -> list[str]:
    """Return a string containing usage information for the given task"""
    lines = []

    lines.append(get_line_task_name(task))
    for flavor in task.flavors.values():

        # if there's only one flavor (the default), don't print the flavor name
        # only print it if there's many flavors
        if flavor.name != "default" or len(task.flavors) > 1:
            flavor_line = get_line_for_flavor(flavor)
            lines.append(" " * indent_level_1 + flavor_line)

        # Print arguments
        for arg in task.arguments:
            line = get_line_for_argument(arg)
            lines.append(" " * indent_level_2 + line)

        lines.append("")

        if print_doctring:
            docstring_lines = task.description_long
            docstring_lines = [" " * indent_level_1 + line for line in docstring_lines]
            lines.extend(docstring_lines)

    return lines
