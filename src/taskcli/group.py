import dataclasses
import typing

if typing.TYPE_CHECKING:
    from .task import Task


created = []


class Group:
    """A group of tasks."""

    def __init__(self, name: str, desc: str = "", hidden: bool = False):
        self.name = name
        self.desc = desc
        self.hidden = hidden
        self.tasks: list["Task"] = []

        global created
        # TODO: this will fail if moduls define groups of same names
        if name in created:
            msg = f"Group {name} already exists"
            raise ValueError(msg)
        created += [name]

    # Make it a context managet
    def __enter__(self) -> "Group":
        global _stack
        _stack.append(self)

        return self

    def __exit__(self, *args: object) -> None:
        global _stack
        _stack.pop()

    def get_name_for_cli(self):
        return self.name.replace(" ", "-").lower()


# Default group for new tasks
NULL_GROUP = Group("null-group")

DEFAULT_GROUP = Group("default", desc="Default tasks")

_stack: list["Group"] = [DEFAULT_GROUP]


def get_current_group() -> "Group":
    """Return the current group."""
    assert len(_stack) > 0
    return _stack[-1]
