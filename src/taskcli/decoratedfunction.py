from .group import Group
from .types import AnyFunction


class DecoratedFunction:
    def __init__(self, func:AnyFunction, group:Group, hidden: bool, important: bool):
        self.func = func
        self.group = group
        self.hidden = hidden
        self.important = important
