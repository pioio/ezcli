import argparse
import typing

if typing.TYPE_CHECKING:
    from .task import Task


class TaskCLI:
    """Configuration of a module which defines tasks."""

    def __init__(self) -> None:
        self.extra_args_list: list[str] = []
        self.tasks: list[Task] = []
        self.hidden_groups: list[str] = []

        # Gets set right before dispatching the function
        self.parsed_args: argparse.Namespace|None = None

    # Any extra arguments passed to the script after a "--"
    # They can be retrieved later to easily inject them to commands being run.
