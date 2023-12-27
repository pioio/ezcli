from typing import Annotated, Any, Iterable, Sequence, TypeVar

from .annotations import Arg
from .parameter import Parameter

T = TypeVar("T")


def arg(
    typevar: T,
    help: str | None = None,
    /,
    # Specific to taskcli
    important: bool = False,
    # forwarded to argparse
    action: str | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | None = None,
    nargs: str | int | None = None,
    default: Any = Parameter.Empty,
) -> Annotated[T, str, Arg]:
    kwargs = locals()

    del kwargs["help"]
    del kwargs["typevar"]
    return Annotated[typevar, help, Arg(**kwargs)]  # type: ignore # noqa: PGH003
