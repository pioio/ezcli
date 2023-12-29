"""Various functions that operate on Tasks."""
from dataclasses import dataclass

from taskcli.task import UserError

from .task import Task
from .taskrendersettings import TaskRenderSettings
import dataclasses
import collections

@dataclass
class FilterResult:
    """Result of filtering tasks."""

    progress: list[str] = dataclasses.field(default_factory=list)
    tasks: list[Task] = dataclasses.field(default_factory=list)
    num_hidden_per_group: dict[str,int] = dataclasses.field(default_factory=lambda: collections.defaultdict(int))
    num_total_hidden: int = 0
    num_total_hidden_in_hidden_groups: int = 0

    hidden_groups:set[str] = dataclasses.field(default_factory=set)
@dataclass
class FilterContext:
    """Current context for filtering tasks.

    This context is here to:
    - reduce number of function params in filter,
    - and make it easier to change filtering later on.
    """

    settings: TaskRenderSettings
    result: FilterResult


def filter_before_listing(tasks: list[Task], settings: TaskRenderSettings) -> FilterResult:
    """Filter tasks before listing them. Applies all possibel filters, but based on Render settings."""
    ctx = FilterContext(settings=settings, result=FilterResult(tasks=tasks))
    ctx.result.progress += [f"Before filtering: {len(ctx.result.tasks)} tasks."]

    _filter_before_listing__hide_tasks_in_hidden_groups(ctx)
    if not ctx.result.tasks:
        return ctx.result

    _filter_before_listing__hide_hidden_tasks(ctx)
    ctx.result.progress += [f"After hiding filtering: {len(ctx.result.tasks)} tasks."]
    if not ctx.result.tasks:
        return ctx.result

    _filter_before_listing__filter_by_tags(ctx)
    if not ctx.result.tasks:
        return ctx.result

    _filter_before_listing__filter_by_search(ctx)

    ctx.result.progress += [f"Final number of tasks: {len(ctx.result.tasks)}."]
    return ctx.result


def _filter_before_listing__hide_tasks_in_hidden_groups(ctx:FilterContext):
    if ctx.settings.show_hidden_groups:
        ctx.result.progress += ["Showing tasks in hidden groups (not hiding them)."]
        return

    visible:list[Task] = []
    for task in ctx.result.tasks:
        if task.is_in_hidden_group():
            ctx.result.hidden_groups.add(task.group.name)
            ctx.result.num_hidden_per_group[task.group.name] += 1
            ctx.result.num_total_hidden_in_hidden_groups +=1
        else:
            visible.append(task)

    ctx.result.tasks = visible
    if not ctx.result.tasks:
        ctx.result.progress += [
            f"No tasks after hiding tasks in hidden groups. All {ctx.result.num_total_hidden_in_hidden_groups} tasks are in hidden groups."]
    else:
        ctx.result.progress += [f"Hidden {ctx.result.num_total_hidden_in_hidden_groups} tasks, {len(ctx.result.tasks)} tasks left."]


def _filter_before_listing__hide_hidden_tasks(ctx:FilterContext):
    if ctx.settings.show_hidden_tasks:
        ctx.result.progress += ["Showing hidden tasks (not hiding them)."]
        return


    visible:list[Task] = []
    for task in ctx.result.tasks:
        if task.is_hidden():
            ctx.result.num_hidden_per_group[task.group.name] += 1
            ctx.result.num_total_hidden +=1
        else:
            visible.append(task)

    ctx.result.tasks = visible
    if not ctx.result.tasks:
        ctx.result.progress += [
            f"No tasks after hiding hidden tasks. All {ctx.result.num_total_hidden} tasks are hidden."]
    else:
        ctx.result.progress += [f"Hidden {ctx.result.num_total_hidden} tasks, {len(ctx.result.tasks)} tasks left."]


def _filter_before_listing__filter_by_tags(ctx:FilterContext):
    if not ctx.settings.tags:
        ctx.result.progress += ["Not filtering by tags."]
        return

    if ctx.settings.tags:
        known_tags: set[str] = set()
        for task in ctx.result.tasks:
            if task.tags:
                known_tags.update(task.tags)
        if known_tags:
            ctx.result.progress += [f"Known tags: {', '.join(known_tags)}"]
        else:
            msg = "Cannot filter by tags: the selected tasks do not have any tags"
            raise UserError(msg)
        ctx.result.tasks = filter_tasks_by_tags(ctx.result.tasks, tags=ctx.settings.tags)

        if not ctx.result.tasks:
            ctx.result.progress += [f"No tasks after filtering by tags ({', '.join(ctx.settings.tags)})"]
        else:
            ctx.result.progress += [f"After filtering by tags ({', '.join(ctx.settings.tags)}): {len(ctx.result.tasks)}."]

def _filter_before_listing__filter_by_search(ctx:FilterContext):
    if not ctx.settings.search:
        ctx.result.progress += ["Not filtering by search."]
        return

    if ctx.settings.search:
        ctx.result.tasks = search_for_tasks(ctx.result.tasks, search=ctx.settings.search)
        if not ctx.result.tasks:
            ctx.result.progress += [f"No tasks after searching name and summary with regex search ({ctx.settings.search})"]
        else:
            ctx.result.progress += [
                f"After searching searching name and summary with regex "
                f"search ({ctx.settings.search}): {len(ctx.result.tasks)}."
            ]


def filter_tasks_by_tags(tasks: list[Task], tags: list[str]) -> list[Task]:
    """Return only tasks which have any of the tags."""
    if not tags:
        return tasks

    filtered = []
    for task in tasks:
        if task.tags:
            for tag in task.tags:
                if tag in tags:
                    filtered.append(task)
                    break
    return filtered


def search_for_tasks(tasks: list[Task], search: str) -> list[Task]:
    """Search for tasks by regex."""
    import re

    try:
        regex = re.compile(search)
    except re.error as e:
        msg = f"Invalid Python regex: {search}"
        raise UserError(msg) from e

    out: list[Task] = []
    for task in tasks:
        if regex.search(task.name):
            out.append(task)
        elif regex.search(task.get_summary_line()):
            out.append(task)

    return out
