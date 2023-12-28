import argparse
from dataclasses import dataclass
from tabnanny import verbose

@dataclass
class TaskRenderSettings:
    show_tags = False
    show_optional_args = False
    show_default_values = False
    show_hidden_groups = False
    show_hidden_tasks = False
    show_ready_env = False
    show_ready_detail:int = 1
    verbose:int = 0


def new_settings(config:argparse.Namespace) -> TaskRenderSettings:
    s = TaskRenderSettings()
    verbose:int = config.verbose

    s.show_tags = config.show_tags or verbose >= 2 or config.list_all

    s.show_optional_args = config.show_optional_args or verbose >= 2 or config.list_all
    s.show_default_values = config.show_default_values or verbose >= 3 or config.list_all

    s.show_hidden_groups = config.show_hidden_groups or verbose >= 3 or config.list_all
    s.show_hidden_tasks = config.show_hidden_tasks or verbose >= 3 or config.list_all

    s.show_ready_detail = config.ready or verbose >= 2 or config.list_all

    s.verbose = verbose

    return s


from typing import Any
import os
