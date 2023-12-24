import inspect

import taskcli

from . import configuration, utils
from .configuration import config
from .decoratedfunction import Task
from .utils import param_to_cli_option

ORDER_TYPE_DEFINITION = "definition"
ORDER_TYPE_ALPHA = "alpha"
ORDER_TYPE_DEFAULT = ORDER_TYPE_ALPHA

ENDC = configuration.get_end_color()


class SafeFormatDict(dict[str, str]):
    """Makes placeholders in a string optional.

    e.g. "Hello {name}" will be rendered as "Hello {name}" if name is not in the dict.
    """

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"  # Return the key as is


def _sort_tasks(tasks: list[Task], sort: str, sort_important_first: str) -> list[Task]:
    names = [task.name for task in tasks]

    presorted = []
    if sort == ORDER_TYPE_ALPHA:
        presorted = sorted(tasks, key=lambda task: task.name)
    else:
        # dont's sort
        presorted = tasks

    if sort_important_first:
        # Bubble the important ones to the top
        tasks = []
        for task in presorted:
            if task.important:
                tasks.append(task)
        for task in presorted:
            if not task.important:
                tasks.append(task)

    return tasks


def list_tasks(tasks: list[Task], verbose: int) -> list[str]:
    """Return a list of lines to be printed to the console."""
    assert len(tasks) > 0, "No tasks found"

    # TODO: extract groups info
    groups = create_groups(tasks=tasks, group_order=configuration.config.group_order)

    # first, prepare rows, row can how more than one line
    lines: list[str] = []

    num_visible_groups = len(
        [group_name for group_name in groups if group_name not in taskcli.get_runtime().hidden_groups]
    )

    for group_name, tasks in groups.items():
        if group_name in taskcli.get_runtime().hidden_groups:
            continue

        if num_visible_groups > 1:
            group_name_rendered = format_colors(config.render_format_of_group_name, name=group_name)
            lines += [group_name_rendered]

        tasks = _sort_tasks(tasks, sort=config.sort, sort_important_first=config.sort_important_first)

        for task in tasks:
            lines.extend(smart_task_lines(task, verbose=verbose))
    lines = [line.rstrip() for line in lines]

    FIRST_LINE_STARTS_WITH_NEW_LINE = lines and lines[0] and lines[0][0] == "\n"  # noqa: N806
    if FIRST_LINE_STARTS_WITH_NEW_LINE:
        # This can happen if user prefixes the custom group format with a "\n" to separate groups with whitesapce
        lines[0] = lines[0][1:]

    return lines


def smart_task_lines(task: Task, verbose: int) -> list[str]:
    """Render a single task into a list of lines, scale formatting to the amount of content."""
    lines: list[str] = []

    name = task.name
    summary = task.get_summary_line()

    max_left = taskcli.config.render_max_left_column_width
    if not summary:
        max_left_if_no_summary = 130
        max_left = max_left_if_no_summary

    line = format_colors(config.render_task_name, name=name)

    include_optional = False
    include_defaults = True

    one_line_params = build_pretty_param_string(
        task, include_optional=include_optional, include_defaults=include_defaults
    )

    potential_line = line + " " + one_line_params
    if len(utils.strip_escape_codes(potential_line)) < max_left:
        line = potential_line
        one_line_params = ""  # clear, to avoid adding it again later

    min_left = taskcli.config.render_min_left_column_width
    line_len = len(utils.strip_escape_codes(line))
    if line_len < min_left:  # add padding before the summary
        line += " " * (min_left - line_len)

    line += summary
    lines.append(line)

    if one_line_params:
        param_line_prefix = "  "
        num_params = len(
            build_pretty_param_list(task, include_optional=include_optional, include_defaults=include_defaults)
        )

        if len(utils.strip_escape_codes(one_line_params)) > 80 or num_params > config.render_max_params_per_line:
            param_list = build_pretty_param_list(
                task, include_optional=include_optional, include_defaults=include_defaults
            )
            for param in param_list:
                lines.append(param_line_prefix + param)
        else:
            lines.append(param_line_prefix + one_line_params)
    return lines


def format_colors(template, **kwargs):
    """Apply colors to a template string of e.g. '{red}foobar{pink}bar."""
    if "name" in kwargs:
        kwargs["NAME"] = kwargs["name"].upper()

    format = SafeFormatDict(clear_format=configuration.colors.end, **kwargs)
    colors = {color: value for color, value in configuration.colors.__dict__.items() if isinstance(value, str)}
    format.update(colors)
    return template.format(**format)


def create_groups(tasks: list[Task], group_order: list[str]) -> dict[str, list[Task]]:
    """Return a dict of group_name -> list of tasks, ordered per group_order, group not listed there will be last."""
    groups: dict[str, list[Task]] = {}
    remaining_tasks: set[Task] = set()
    for expected_group in group_order:
        for task in tasks:
            if task.group.name == expected_group:
                if expected_group not in groups:
                    groups[expected_group] = []
                groups[expected_group].append(task)
            else:
                remaining_tasks.add(task)
    for task in remaining_tasks:
        if task.group.name not in groups:
            groups[task.group.name] = []
        groups[task.group.name].append(task)
    return groups


def build_pretty_param_string(task: Task, include_optional: bool = True, include_defaults: bool = True) -> str:
    """Return a string with all params, formatted for the console."""
    endc = configuration.get_end_color()
    pretty_params = build_pretty_param_list(task, include_optional=include_optional, include_defaults=include_defaults)
    return f"{config.render_color_summary}, {endc}".join(pretty_params)


def build_pretty_param_list(  # noqa: C901
    task: Task, include_optional: bool = True, include_defaults: bool = True, truncate_long: bool = True
) -> list[str]:
    end_color = configuration.get_end_color()

    pretty_params = []
    for param in task.params:
        #    if not include_optional and param_has_a_default and (param.name not in config.render_always_show_args):
        if not include_optional and param.has_default() and not param.important:
            # skip args which have a default value specified
            continue

        if param.has_default() and param.name in config.render_hide_optional_args:
            continue
        rendered = param.name

        if param.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
            rendered = rendered.upper()
        elif param.kind in [inspect.Parameter.KEYWORD_ONLY]:
            rendered = param_to_cli_option(rendered)

        if not param.has_default():
            rendered = f"{config.render_color_mandatory_arg}{rendered}{end_color}"
        else:
            rendered = f"{config.render_color_optional_arg}{rendered}{end_color}"

        if param.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
            rendered = rendered

        elif param.kind in [inspect.Parameter.KEYWORD_ONLY]:
            rendered = param_to_cli_option(param.name)
        elif param.kind in [inspect.Parameter.VAR_POSITIONAL]:
            rendered = f"*{param.name}"
        elif param.kind in [inspect.Parameter.VAR_KEYWORD]:
            rendered = f"**{param.name}"
        else:
            msg = f"Unknown parameter kind: {param.kind}"
            raise Exception(msg)

        if include_defaults and not param.type == bool:
            if param.has_default():
                # Shorten default value
                default_value = param.default
                if truncate_long:
                    if len(str(default_value)) > config.render_max_default_arg_width:
                        default_value = str(default_value)[: config.render_max_default_arg_width] + "..."

                rendered += f"{config.render_color_optional_arg}={end_color}{config.render_color_default_arg}{default_value}{end_color}"
            else:
                rendered += ""
        pretty_params.append(rendered)

    return pretty_params
