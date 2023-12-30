import dataclasses
from dataclasses import dataclass

from .taskcliconfig import TaskCLIConfig


@dataclass
class TaskRenderSettings:
    """Configuration for how to render list of tasks.

    The values below are set based on settings in the TaskCLIConfig object.
    """

    show_tags = False
    show_optional_args = False
    show_default_values = False
    show_hidden_groups = False
    show_hidden_tasks = False
    show_ready_info = False
    show_include_info = False
    group_order:list[str] = dataclasses.field(default_factory=list)
    tags: list[str] = dataclasses.field(default_factory=list)
    search: str = ""
    verbose: int = 0


def new_settings(config: TaskCLIConfig) -> TaskRenderSettings:
    """Translate the initial runtime configuration into which elements to show when listing tags.

    This is a nice layer of indirection.
    Good to have as as various aspects of the render settings can be influenced by many different runtime settings.
    Having all this here helps to keep
     1) keep the entire logic together
     2) keeps the code for listing tasks much cleaner.
    """
    s = TaskRenderSettings()
    verbose: int = config.verbose

    s.show_tags = config.show_tags or verbose >= 2 or config.list_all or config.list >= 2

    s.show_optional_args = config.show_optional_args or verbose >= 2 or config.list_all or config.list >= 2
    s.show_default_values = config.show_default_values or verbose >= 3 or config.list_all or config.list >= 3

    s.show_hidden_groups = (
        config.show_hidden_groups or verbose >= 3 or config.list_all or config.show_hidden or config.list >= 3
    )
    s.show_hidden_tasks = (
        config.show_hidden_tasks or verbose >= 3 or config.list_all or config.show_hidden or config.list >= 3
    )

    s.show_ready_info = config.show_ready_info or verbose >= 2 or config.list_all or config.list >= 2

    s.verbose = verbose
    s.tags = config.tags

    s.search = config.search

    s.show_include_info = verbose >= 3 or config.list_all or config.list >= 3

    # Always show hidden tasks and groups when filtering by tags or searching.
    if config.tags or config.search:
        s.show_hidden_tasks = True
        s.show_hidden_groups = True

    s.group_order = config.group_order
    return s
