import dataclasses
import typing

from .logging import get_logger
from .utils import get_callers_module

if typing.TYPE_CHECKING:
    from .task import Task


created = []
_is_init = True


log = get_logger(__name__)


class Group:
    """A group of tasks."""

    def __init__(
        self,
        name: str,
        desc: str = "",
        hidden: bool = False,
        sort_hidden_last: bool = False,
        sort_important_first: bool = False,
        name_namespace: str = "",
        alias_namespace: str = "",
        from_parent: bool = False,
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
            from_parent: If true, this group was included from a taskfile loaded from above/parent directory
        """
        self.name = name
        self.desc = desc
        self.hidden = hidden
        self.tasks: list["Task"] = []

        self.name_namespace: str = name_namespace
        self.alias_namespace: str = alias_namespace

        self.sort_important_first = sort_important_first
        self.sort_hidden_last = sort_hidden_last

        self.from_parent = from_parent

        global created
        # TODO: this will fail if moduls define groups of same names
        if name in created:
            msg = f"Group {name} already exists"
            log.debug(msg)
        # > need to disable, otherwise triggers when merge with parents whcih imports from child
        # >        raise ValueError(msg)
        created += [name]

        self.parent: Group | None = None
        self.children: list[Group] = []

    # Make it a context managet
    def __enter__(self) -> "Group":
        global _stack
        parent_module = get_callers_module()

        if parent_module not in _stacks:
            _stacks[parent_module] = [Group("default", desc="Default tasks")]

        # nested groups
        if len(_stacks[parent_module]) > 1:  # one (default) is always there
            self.parent = _stacks[parent_module][-1]
            self.parent.children.append(self)

        _stacks[parent_module].append(self)

        return self

    def __repr__(self) -> str:
        return f"Group({self.name}, hidden={self.hidden})"

    def __exit__(self, *args: object) -> None:
        global _stack
        parent_module = get_callers_module()
        _stacks[parent_module].pop()

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

    def has_children_recursive(self, tasks: list["Task"]) -> bool:
        """Return True if this group, or any of its children, has any of the given tasks.

        Used for selecting groups to show in the list.
        """
        if any(task in tasks for task in self.tasks):
            return True
        for child in self.children:
            if child.has_children_recursive(tasks):
                return True

        return False


# Default group for new tasks
#NULL_GROUP = Group("null-group")

#DEFAULT_GROUP = Group("default", desc="Default tasks")

#_stack: list["Group"] = [DEFAULT_GROUP]
_stacks: dict[typing.Any, list["Group"]] = {}

def get_current_group(module) -> "Group":
    """Return the current group."""

    if module not in _stacks:
        _stacks[module] = [Group("default", desc="Default tasks")]

    assert len(_stacks[module]) > 0
    return _stacks[module][-1]


def get_all_groups_from_tasks(tasks: list["Task"]) -> list["Group"]:
    """Return a list of groups that contain any of the given tasks. Including any grandparent groups."""
    groups = []
    for task in tasks:
        for group in task.groups:
            if group not in groups:
                groups.append(group)
    return groups


def get_all_tasks_in_group(group: "Group", tasks: list["Task"]) -> None:
    """Recursive populate the given list of tasks with all tasks in the given group (inc grandchildren)."""
    for task in group.tasks:
        if task not in tasks:
            tasks.append(task)
    for child in group.children:
        get_all_tasks_in_group(child, tasks)
