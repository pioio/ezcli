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
    type: Any = Parameter.Empty,
) -> Annotated[T, str, Arg]:
    """Create an annotated type with an Arg annotation.

    the Arg() objects get stored in task.param[].arg_annotation

    Examples
      - arg(int, "The number of foos in the bar", important=True)
      - arg(int, "The number of foos in the bar")

    """
    kwargs = locals()

    del kwargs["help"]
    del kwargs["typevar"]
    return Annotated[typevar, help, Arg(**kwargs)]  # type: ignore # noqa: PGH003
