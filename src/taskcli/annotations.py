from dataclasses import dataclass
from typing import Any, Iterable


# We need a special class to denote default not being set, as a "None" can also be a default
class Empty:
    """Indicates that a default value is not set."""


@dataclass
class Arg:
    """A task argument."""

    name: str = ""
    important: bool = False
    has_default: bool = False
    is_kwarg: bool = False
    default: Any = Empty

    # argparse
    action: str | None = None
    choices: Iterable[Any] | None = None
    metavar: str | None = None
    nargs: str | int | None = None
    type: Any = None

    def get_argparse_fields(self) -> dict[str, Any]:
        """Return a dict of fields which can be passed to argparse.add_argument."""
        out: dict[str, Any] = {}

        from .parameter import Parameter

        if self.action is not None:
            out["action"] = self.action
        if self.choices is not None:
            out["choices"] = self.choices
        if self.metavar is not None:
            out["metavar"] = self.metavar
        if self.nargs is not None:
            out["nargs"] = self.nargs
        if self.type is not None and self.type is not Parameter.Empty:
            out["type"] = self.type

        # Don't return the default here, it's special, as it can also be set in function signature

        return out
