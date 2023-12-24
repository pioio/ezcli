import dataclasses


@dataclasses.dataclass
class Group:
    """A group of tasks."""

    name: str
    hidden: bool = False
