# name, desc


import dataclasses
# ENABLE_COLORS = config.render_colors == "auto" and sys.stdout.isatty() or config.render_colors == "always"
import sys
from typing import Any, Callable  # noqa: F401

LIST_DETAILS_LOW = 0

# Name   desc  mandatory args
LIST_DETAILS_MEDIUM = 1  # Default


# Name desc all args
LIST_DETAILS_HIGH = 2  # -vv


# name desc all args + defaults
LIST_DETAILS_ULTRA = 3  # -vvv

COLOR_NONE = ""
COLOR_DARK_GRAY = "\033[90m"
COLOR_WHITE = "\033[97m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_END = "\033[0m"
COLOR_UNDERLINE = "\033[4m"


@dataclasses.dataclass
class Colors:
    none: str = COLOR_NONE
    dark_gray: str = COLOR_DARK_GRAY
    white: str = COLOR_WHITE
    yellow: str = COLOR_YELLOW
    green: str = COLOR_GREEN
    end: str = COLOR_END
    blue: str = "\033[94m"
    red: str = "\033[91m"
    underline: str = COLOR_UNDERLINE


colors = Colors()


ENABLE_COLORS = sys.stdout.isatty()
if not ENABLE_COLORS:
    # for attr in dir(config):
    #     if attr.startswith("render_color_"):
    #         setattr(config, attr, "")
    for key, value in colors.__dict__.items():
        if key.startswith("__"):
            continue
        setattr(colors, key, "")


@dataclasses.dataclass
class Config:
    # The order of groups of tasks when list
    # All tasks are by default in the "default" group unless task(group="foo") is used
    # Any group not listed here will be shown last, in the order they were defined.
    group_order: list[str] = dataclasses.field(default_factory=lambda: ["default"])

    render_color_mandatory_arg: str = colors.yellow
    render_color_optional_arg: str = colors.dark_gray
    render_color_default_arg = colors.dark_gray + colors.underline
    render_color_task_name: str = colors.green
    render_color_summary: str = colors.white
    render_color_namespace: str = colors.none
    render_color_group_name: str = colors.white
    render_extra_line_indent: str = "    "
    render_prefix: str = f"{colors.yellow}*{colors.end} "

    # Always show these args in the task list, even if they are optional
    render_always_show_args: list[str] = dataclasses.field(default_factory=list)

    # Use to hide rarely used params,or params with long, names from the task list to reduce the noise
    # Hidden params still show up in the tab completion.
    # TODO make work
    # XXXXXXXXx
    # TODO hightlight soome arguments in special color
    render_highligh_params: dict[str,str] = dataclasses.field(default_factory=dict)
    # foo = {"force": colors.red}
    render_hide_optional_args: list[str] = dataclasses.field(default_factory=list)

    render_format_of_important_tasks: str = "{red}{name}{clear_format}"

    # The left column (with task name and args) will pref
    # Only rows with very long task names will be longer than this.
    # If your task have many manadatory arguments, you may want to increase
    # this to vertically align the summaries of tasks.
    render_max_left_column_width: int = 30

    # The left column will never be smaller than this, even with short task names
    # Increaase it if you prefer your summaries to be more to the right.
    render_min_left_column_width: int = 20

    # The column with the task name will never be shorter than this
    # Increasing this will the start of arg listing to the right.
    render_min_task_name: int = 10

    # The amount of info to show by default when running task list
    render_default_list_details: int = LIST_DETAILS_MEDIUM
    render_colors = "auto"  # "auto", "always", or "never"

    # Default args longer than this will be truncated

    render_max_default_arg_width: int = 20

    # -1 for full terminal width
    render_group_header_len: int = 40

    #####################################################################
    # Advanced config options

    # if true, @task function prefixed with "_" will be marked as hidden
    adv_hide_private_tasks: bool = True
    show_hidden_tasks: bool = False

    adv_render_separator_line_char: str = "="

    # Python string format for the separator line
    # justify name center
    adv_render_separator_line_title: str = "{underline}{white}*** {underline}{name}{clear_format}"
    # adv_render_separator_line_title:str = "{line_chars}"


config = Config()



def get_end_color() -> str:
    if ENABLE_COLORS:
        return colors.end
    return ""


def get_underline() -> str:
    if ENABLE_COLORS:
        return COLOR_UNDERLINE
    return ""


_list_details = 0

_set_list_show_args = None


def set_list_render_fun(callable:Any) -> None:
    global _set_list_show_args
    _set_list_show_args = callable
