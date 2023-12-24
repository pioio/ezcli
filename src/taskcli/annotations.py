from dataclasses import dataclass
from typing import Any



class Arg:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


@dataclass
class Help:
    """Help"""
    text: str

@dataclass
class Choice:
    """Help"""
    text: list[Any]
