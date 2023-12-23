import dataclasses


@dataclasses.dataclass
class Group:
    name: str
    hidden: bool = False
