import types
from typing import Any, Callable

AnyFunction = Callable[..., Any]
Module = types.ModuleType

# if typing.TYPE_CHECKING:
#     from .task import Task
#     from .group import Group

# class Module2(types.ModuleType):
#     """A Python module with an interface for storing tasks."""

#     def __init__(self):
#         self.tasks: list[Task] = []
#         self.groups: list[Group] = []



__all__ = [
    "AnyFunction",
    "Module",
    "Any",
    "Callable",
]


class UserError(Exception):
    """Print nice error to the user."""
