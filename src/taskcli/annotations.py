from dataclasses import dataclass
from typing import Any, Iterable


# We need a special class to denote default not being set, as a "None" can also be a default
class Empty:
    pass

@dataclass
class Arg:
    name: str = ""
    default: Any = Empty
    important: bool = False
    has_default: bool = False
    is_kwarg: bool = False

    # argparse
    action:str|None=None
    choices:Iterable[Any]|None=None
    metavar:str|None=None
    nargs:str|int|None=None
    default:Any=None

    def get_argparse_fields(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "choices": self.choices,
            "metavar": self.metavar,
            "nargs": self.nargs,
            "default": self.default,
        }



@dataclass
class Help:
    """Help"""
    text: str

@dataclass
class Choice:
    """Help"""
    text: list[Any]
