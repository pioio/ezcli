import inspect
import typing
from math import e
from operator import is_
from types import UnionType
from typing import Any, List, TypeVar, Union, get_args, get_origin
from webbrowser import get

from . import annotations
from .parametertype import ParameterType
from .utils import param_to_cli_option

# So that we don't duplicate the default value of arg annotation
default_arg_annotation = annotations.Arg()


class Parameter:
    """A wrapper around inspect.Parameter to make it easier to work with."""

    class Empty:
        """A class to represent an empty value."""

    POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
    KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
    VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
    VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD

    def __init__(self, param: inspect.Parameter):
        """Read the parameter and stores the information in this class for easier access."""
        # original inspect.Parameter
        self.param: inspect.Parameter = param

        param_using_typing_annotated = getattr(param.annotation, "__metadata__", None) is not None

        # Metadata coming from typing.Annotated, empty list if not using it
        self.metadata: list[Any] = [] if not param_using_typing_annotated else param.annotation.__metadata__

        # The Arg annotation, if present, can cantain various additional options
        self.arg_annotation: annotations.Arg | None = None
        for data in self.metadata:
            if isinstance(data, annotations.Arg):
                self.arg_annotation = data
                break

        self.kind = param.kind
        assert self.kind in [
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ]

        # type can come from three places
        # 1. The annotation  (foobar: int)
        # ### 2. The default value (foobar=5)
        # 3. The Arg annotation (foobar: annotations.Arg[int])
        # ### 4. The Arg annotation default (foobar: annotations.Arg[int, arg(default=5)])
        # If both are present, the annotation takes precedence
        the_type = param.annotation if not param_using_typing_annotated else param.annotation.__origin__

        self.help: str | None = None
        for data in self.metadata:  # Find the help string in annotation
            if isinstance(data, str):
                self.help = data
                break

        # Default value is either in the in the signature (precedence), or
        # in the custom arg annotation (where it can be a shared default for many parameters)
        self.default: Any = Parameter.Empty
        if param.default is not inspect.Parameter.empty:
            self.default = param.default
        elif self.arg_annotation:
            if self.arg_annotation.default is not annotations.Empty:
                self.default = self.arg_annotation.default

        self.type = ParameterType(the_type, default_value=self.default, arg_annotation=self.arg_annotation)

        self.name = param.name

    def is_positional(self) -> bool:
        """Return True if the parameter is positional, False if it is keyword-only (i.e. requiring --flag)."""
        return self.kind in [
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.VAR_KEYWORD,  # ??? not sure ...
        ]

    @property
    def important(self) -> bool:
        """Return True if the parameter is marked as important."""
        return self.arg_annotation.important if self.arg_annotation else default_arg_annotation.important

    def has_default(self) -> bool:
        """Return True if the parameter has a default value."""
        return self.default is not Parameter.Empty

    def get_argparse_names(self, known_short_args: set[str]) -> list[str]:
        """Return the names for argparse, in order of precedence."""
        # TODO: return single flag params also
        out = []
        if self.is_positional():
            name = self.name
            out += [name]
            assert "-" not in name, "for positional, we need underscores, not dashes "
        else:
            name = param_to_cli_option(self.name)
            out += [name]

            # Now come up with a unique short flag (used ones were provided via known_short_args)
            candidate1 = "-" + self.name[0].lower()
            candidate2 = "-" + self.name[0].upper()
            if candidate1 not in known_short_args:
                out += [candidate1]
            elif candidate2 not in known_short_args:
                out += [candidate2]
            else:
                # we tried, don't add any short flag
                pass

            assert "_" not in name, "for options, we need dashes, not underscores"

        return out
