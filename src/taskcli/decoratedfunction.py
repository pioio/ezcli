from .group import Group
from .types import AnyFunction


class DecoratedFunction:
    def __init__(self, func:AnyFunction, group:Group, hidden: bool, important: bool):
        self.func = func
        self.group = group
        self.hidden = hidden
        self.important = important

    def is_hidden(self) -> bool:
        return self.hidden or self.func.__name__.startswith("_")

    def get_full_task_name(self) -> str:
        out = self.func.__name__.replace("_", "-")
        out.lstrip("-") # for _private functions

        if self.hidden:
            out = "_" + out
        return out