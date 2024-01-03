import typing

#from .types import Module2

if typing.TYPE_CHECKING:
    import argparse

    from .task import Task

from dataclasses import dataclass, field
@dataclass
class InitStats:
    """Summary of what happened during initialization of the runtime."""
    inspected_files: list[str] = field(default_factory=list)
    parent_taskfile_path: str = ""




class TaskCLI:
    """Configuration of a module which defines tasks."""

    def __init__(self) -> None:
        self.extra_args_list: list[str] = []
        self.tasks: list[Task] = []
        self.hidden_groups: list[str] = []

        # Gets set right before dispatching the function
        self.parsed_args: argparse.Namespace | None = None

        self.overview: str = ""

        self.current_tasks: list[Task] = []

        self.init_stats = InitStats()

#        self.modules: dict[str,Module2] = {}

    # Any extra arguments passed to the script after a "--"
    # They can be retrieved later to easily inject them to commands being run.
