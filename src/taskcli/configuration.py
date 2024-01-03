import dataclasses
import sys

from . import envvars
from .timer import Timer

COLOR_NONE = ""
COLOR_DARK_GRAY = "\033[90m"
COLOR_WHITE = "\033[97m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_END = "\033[0m"
COLOR_UNDERLINE = "\033[4m"

@dataclasses.dataclass
class Colors:
    """Colors used for rendering the task list.

    Names of fields from this class can be used as '{color}' value in
    the RenderConfig object string format fields.
    """

    none: str = COLOR_NONE
    dark_gray: str = COLOR_DARK_GRAY
    white: str = COLOR_WHITE
    yellow: str = COLOR_YELLOW
    green: str = COLOR_GREEN
    pink: str = "\033[95m"
    end: str = COLOR_END
    blue: str = "\033[94m"
    red: str = "\033[91m"
    underline: str = COLOR_UNDERLINE
    bold: str = "\033[1m"



colors = Colors()

ENABLE_COLORS = sys.stdout.isatty()

if not ENABLE_COLORS:
    for key, _ in colors.__dict__.items():
        if key.startswith("__"):
            continue
        setattr(colors, key, "")

from typing import Any, Generic, TypeVar, Type

T = TypeVar("T")
import json

class _Field(Generic[T]):
    def __init__(self, value: T, /, desc: str = "", type_: Type|None = None, env: bool = True):
        self.value = value

        self.desc = desc.lstrip().rstrip()

        # Strip '        ' from the start of each line
        self.desc = "\n".join([line[8:] if line.startswith("        ") else line for line in self.desc.splitlines()])

        self.type = type_ if type_ else type(value)
        self.env = env

    def __get__(self, obj: Any, type: Any = None) -> T:
        return getattr(obj, '_' + self.name, self.value)

    def __set__(self, obj: Any, value: T) -> None:
        setattr(obj, '_' + self.name, value)

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name

    def get_env_name(self, obj: Any) -> str:
        return "TASKCLI_ADV_" + self.name.upper()

    def cast(self, value: str) -> T:
        if self.type == list:
            return json.loads(value)
        elif self.type in [int, float, bool]:
            return self.type(value)

        raise Exception(f"Unhandled type {self.type}")
        return value  # Fallback for strings and unhandled types




class AdvConfig:
    """Advanced Config.

    You rarely need to change these settings, but you can if you e.g. want o create custom themes
    for your taskfiles.
    """

    # # The order of groups of tasks when list
    # # All tasks are by default in the "default" group unless task(group="foo") is used
    # # Any group not listed here will be shown last, in the order they were defined.

    render_color_mandatory_arg = _Field(colors.yellow)
    render_color_optional_arg = _Field(colors.dark_gray)
    render_color_optional_and_important_arg = ""
    render_color_default_arg = _Field(colors.dark_gray + colors.underline)
    render_color_summary = _Field(colors.end)
    render_extra_line_indent = _Field("  ")

    render_format_regular_task_name = _Field("{green}{name}{clear}")
    render_format_important_tasks = _Field("{green}{bold}{underline}{name}{clear}")
    render_format_hidden_tasks = _Field("{dark_gray}{name}{clear}")
    render_format_included_taskfile_dev_task = _Field("{blue}{name}{clear}")

    # Always show these args in the task list, even if they are optional
    render_always_show_args = _Field[list[str]]([], "Always show these args in the task list, even if they are optional")

    # Use to hide rarely used params,or params with long, names from the task list to reduce the noise
    # Hidden params still show up in the tab completion.

    # TODO hightlight soome arguments in special color
    render_highligh_params = _Field[dict[str,str]]({})


    render_hide_optional_args = _Field[list[str]]([], desc="""
        Never show optional arguments which have this name.
        Useful if many tasks have repeating, rarely used, optional arguments which we never.
        want to see in the task list.""")

    # use {NAME} instead of {name} to print group name in uppercase
    render_format_of_group_name = _Field("{bold}{icon}{name:<22}{desc:<10}{clear}")
    render_format_of_group_name_hidden = _Field("{dark_gray}{bold}{name:<22}{desc:<10}{clear}")


    render_max_left_column_width = _Field(22, desc="""
        The left column (with task name and args) will pref
        Only rows with very long task names will be longer than this.
        If your task have many manadatory arguments, you may want to increase
        this to vertically align the summaries of tasks.""")

    # The left column will never be smaller than this, even with short task names
    # Increaase it if you prefer your summaries to be more to the right.
    render_min_left_column_width = _Field(22)


    render_max_params_per_line = _Field(5, desc="""
        Any tasks with more rendered params then this will be split into multiple lines""")

    render_max_default_arg_width = _Field(40, desc="Default args longer than this will be truncated")

    sort = _Field("alpha", desc="Sort order")  # "alpha"  "definition")

    # If true, @task functions prefixed with "_" will be marked as hidden by default
    # No need to use hidden=True
    # e.g.
    #   @task
    #   def _mytask():
    #     ...
    auto_hide_private_tasks = _Field(True)

    # When set, it will be added
    name_namespace_separator = _Field(".")

    # When set, it will be added between the alias and the task name
    # By default it's empty, as it's often desired to keep aliases short and easy to type
    alias_namespace_separator = _Field("")


with Timer("Init Advanced config"):
    adv_config = AdvConfig()


def apply_simple_formatting() -> None:
    """Change the formatting to make the output simpler.

    This is useful for (and used by) unit tests to keep their assertions simpler.
    """
    adv_config.render_format_important_tasks = "{name}"
    adv_config.render_format_regular_task_name = "{name}"
    adv_config.render_format_hidden_tasks = "{name}"
    adv_config.render_format_included_taskfile_dev_task = "{name}"
    adv_config.render_format_of_group_name = "# {name}"
    adv_config.render_format_of_group_name_hidden = "# {name} HIDDEN"


if envvars.TASKCLI_ADV_OVERRIDE_FORMATTING.is_true():
    apply_simple_formatting()


def get_end_color() -> str:
    """Return the escape code to reset the terminal color."""
    if ENABLE_COLORS:
        return colors.end
    return ""


def get_underline() -> str:
    """Return the escape code to underline the text."""
    if ENABLE_COLORS:
        return COLOR_UNDERLINE
    return ""
