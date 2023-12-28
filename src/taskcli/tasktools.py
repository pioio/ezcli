"""Various functions that operate on Tasks."""
from dataclasses import dataclass

from taskcli.task import UserError

from .task import Task
from .taskrendersettings import TaskRenderSettings


@dataclass
class FilterResult:
    """Result of filtering tasks."""

    tasks: list[Task]
    progress: list[str]


def filter_before_listing(tasks: list[Task], settings: TaskRenderSettings) -> FilterResult:
    """Filter tasks before listing them."""
    progress = []
    progress += [f"Before filtering: {len(tasks)}."]



    if settings.tags:
        known_tags:set[str] = set()
        for task in tasks:
            if task.tags:
                known_tags.update(task.tags)
        if known_tags:
            progress += [f"Known tags: {', '.join(known_tags)}"]
        else:
            msg = "Cannot filter by tags: the selected tasks do not have any tags"
            raise UserError(msg)
        filtered_tasks = filter_tasks_by_tags(tasks, tags=settings.tags)
        if not filtered_tasks:
            progress += [f"No tasks after filtering by tags ({', '.join(settings.tags)})"]
            return FilterResult(tasks=[], progress=progress)

        progress += [f"After filtering by tags ({', '.join(settings.tags)}): {len(filtered_tasks)}."]
    else:
        filtered_tasks = tasks

    if settings.search:
        search_filtered_tasks = search_for_tasks(tasks=filtered_tasks, search=settings.search)
        if not search_filtered_tasks:
            progress += [f"No tasks after searching name and summary with regex search ({settings.search})"]
            return FilterResult(tasks=[], progress=progress)
        progress += [
            f"After searching searching name and summary with regex "
            f"search ({settings.search}): {len(search_filtered_tasks)}."
        ]
    else:
        search_filtered_tasks = filtered_tasks

    progress += [f"Final number of tasks: {len(search_filtered_tasks)}."]
    return FilterResult(tasks=search_filtered_tasks, progress=progress)


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
