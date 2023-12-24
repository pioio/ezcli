
from .decoratedfunction import DecoratedFunction


class TaskCLI:
    def __init__(self) -> None:
        self.extra_args_list:list[str] = []
        self.tasks:list[DecoratedFunction] = []

    # Any extra arguments passed to the script after a "--"
    # They can be retrieved later to easily inject them to commands being run.
