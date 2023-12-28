import argparse
from dataclasses import dataclass
from tabnanny import verbose
import dataclasses

from .envvar import EnvVar

@dataclass
class TaskRenderSettings:
    show_tags = False
    show_optional_args = False
    show_default_values = False
    show_hidden_groups = False
    show_hidden_tasks = False
    show_ready_info = False
    tags:list[str] = dataclasses.field(default_factory=list)
    verbose:int = 0


from .taskcliconfig import TaskCLIConfig


def new_settings(config:TaskCLIConfig) -> TaskRenderSettings:
    """Translate the initial runtime configuration into which elements to show when listing tags."""
    s = TaskRenderSettings()
    verbose:int = config.verbose

    s.show_tags = config.show_tags or verbose >= 2 or config.list_all or config.list >= 2

    s.show_optional_args = config.show_optional_args or verbose >= 2 or config.list_all or config.list >= 2
    s.show_default_values = config.show_default_values or verbose >= 3 or config.list_all or config.list >= 3

    s.show_hidden_groups =  config.show_hidden_groups or verbose >= 3 or config.list_all or config.show_hidden or config.list >= 3
    s.show_hidden_tasks = config.show_hidden_tasks or verbose >= 3 or config.list_all or config.show_hidden or config.list >= 3

    s.show_ready_info = config.show_ready_info or verbose >= 2 or config.list_all or config.list >= 2

    s.verbose = verbose
    s.tags = config.tags

    return s


from typing import Any
import os
