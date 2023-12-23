import types
from typing import Any, Callable

AnyFunction = Callable[..., Any]
Module = types.ModuleType

__all__ = ["AnyFunction", "Module", "Any", "Callable"]
