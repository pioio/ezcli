import dataclasses
import typing

if typing.TYPE_CHECKING:
    from .task import Task


created = []


class Group:
    """A group of tasks."""

    def __init__(
        self,
        name: str,
        desc: str = "",
        hidden: bool = False,
        sort_hidden_last: bool = True,
        sort_important_first: bool = True,
        namespace: str = "",
        alias_namespace: str = "",
    ):
        """Create a new group of tasks.

        Args:
            name: Name of the group
            desc: one-line description of the group, seen in the task list
            hidden: If true, the group is hidden by default
            sort_hidden_last: If true, hidden tasks are sorted last (after all other tasks)
            sort_important_first: If true, important tasks are sorted as first (before all other tasks)
            namespace: namespaces prepended to all tasks added to this group
            alias_namespace: namespace prepended to all aliases of tasks added to this group
        """
        self.name = name
        self.desc = desc
        self.hidden = hidden
        self.tasks: list["Task"] = []

        self.namespace: str = namespace
        self.alias_namespace: str = alias_namespace

        self.sort_important_first = sort_important_first
        self.sort_hidden_last = sort_hidden_last

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

    def __repr__(self) -> str:
        return f"Group({self.name}, hidden={self.hidden})"

    def __exit__(self, *args: object) -> None:
        global _stack
        _stack.pop()

    def get_name_for_cli(self) -> str:
        """Return the name of the group suitable for CLI completion."""
        return self.name.replace(" ", "-").lower()

    def render_num_shown_hidden_tasks(self) -> str:
        """Return a string showing the number of shown and hidden tasks."""
        num_hidden = len([task for task in self.tasks if task.hidden])
        num_shown = len([task for task in self.tasks if not task.hidden])
        if num_hidden == 0:
            return f"{num_shown}"
        else:
            return f"{num_shown}/{num_shown+num_hidden}"


# Default group for new tasks
NULL_GROUP = Group("null-group")

DEFAULT_GROUP = Group("default", desc="Default tasks")

_stack: list["Group"] = [DEFAULT_GROUP]


def get_current_group() -> "Group":
    """Return the current group."""
    assert len(_stack) > 0
    return _stack[-1]
