import inspect

from .group import Group
from .parameter import Parameter
from .types import AnyFunction


class Task:
    """A decorated function."""
    def __init__(self, func:AnyFunction, group:Group|None=None, hidden: bool=False, important: bool=False):
        """

        Args:
            func: The decorated python function.
            hidden: If True, the task will not be listed in the help by default.
            important: If True, the task will be listed in the help in a way which stands out. See config for details.
        """
        self.func = func
        self.group = group or Group("default")
        self.hidden = hidden
        self.important = important
        self.params = [Parameter(param) for param in inspect.signature(func).parameters.values()]

    def is_hidden(self) -> bool:
        return self.hidden or self.func.__name__.startswith("_")

    @property
    def name(self) -> str:
        return self.get_full_task_name()

    def get_full_task_name(self) -> str:
        out = self.func.__name__.replace("_", "-")
        out.lstrip("-") # for _private functions

        if self.hidden:
            out = "_" + out
        return out

    def get_summary_line(self) -> str:
        """Return the first line of docstring, or empty string if no docstring."""
        if self.func.__doc__ is None:
            return ""
        return self.func.__doc__.split("\n")[0]
