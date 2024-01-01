import types
from typing import Any, Callable

AnyFunction = Callable[..., Any]
Module = types.ModuleType


class Module2(types.ModuleType):
    """A Python module with an interface for storing tasks."""

    # TODO


__all__ = [
    "AnyFunction",
    "Module",
    "Any",
    "Callable",
]
