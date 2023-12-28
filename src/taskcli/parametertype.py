from typing import Any
import inspect
from typing import Union, get_args, get_origin
from types import UnionType
import typing
if typing.TYPE_CHECKING:
    from .parameter import Parameter

class ParameterType:
    """A class to represent the type of a parameter."""

    class Empty:
        """A class to represent that type was not set."""

    def __init__(self, typevar:Any, /,*, default_value:Any):
        self._type = typevar
        from .parameter import Parameter
        if self._type is inspect.Parameter.empty:
            self._type = ParameterType.Empty
        if self._type is Parameter.Empty:
            self._type = ParameterType.Empty

        self._default_value = default_value  # default value of the parameter

    @property
    def raw(self) -> Any:
        """Return the original type."""
        return self._type

    def was_specified(self) -> bool:
        """Return True if the type was specified explicitly."""
        return self._type is not ParameterType.Empty

    def has_supported_type(self) -> bool:
        """Return True if the type of the parameter is supported by taskcli (in the context of adding it to argparse).

        If param has unsupported type, but a default value, the task can be still be run,
        but the parameter will not be added to argparse.
        """
        from .parameter import Parameter

        if self._type is ParameterType.Empty:
            # no type annotation, will assume it's a string
            return True

        if self.is_union_list_none():
            return True

        if self.is_list():
            type_of_list = self.get_list_type_args()
            if type_of_list in [int, float, str]:
                return True
            elif type_of_list is None:
                return True
            else:
                return False

        if self._type in [int, float, str, bool]:
            return True

        return False

    def is_union_list_none(self) -> bool:
        """Return True if the parameter is a union of list and None."""
        if self._type is inspect.Parameter.empty:
            return False

        if self.is_union_of(list, None.__class__):
            return True

        if self.is_union():
            union_args = get_args(self._type)
            if len(union_args) == 2:
                foundlist = False
                foundnone = False
                for arg in union_args:
                    if get_origin(arg) is list:
                        foundlist = True
                    if arg is None.__class__:
                        foundnone = True
                if foundlist and foundnone:
                    return True

        return False

    def is_union(self) -> bool:
        """Return True if the parameter type is a union.

        Python has two union syntaxes:
           'get_origin(self.annotation) is Union'  ->   python 3.9 syntax, Union[list|None]
           'isinstance(self.annotation, UnionType)'  ->   python 3.10 syntax,  list|None
        """
        return get_origin(self._type) is Union or isinstance(self._type, UnionType)

    def is_union_of(self, typevar1: Any, typevar2: Any) -> bool:  # "None.__class__" for non
        """Return True if the parameter type is a union of the two specified types."""
        assert typevar1 is not None, "use   None.__class__ for None"
        assert typevar2 is not None, "use   None.__class__ for None"
        if not self.is_union():
            return False
        if get_args(self._type) == (typevar1, typevar2) or get_args(self._type) == (typevar2, typevar1):
            return True
        return False

    def is_bool(self) -> bool:
        """Return True if the parameter type is bool."""
        from .parameter import Parameter
        if self._type is bool:
            # type set explicitly
            return True
        if self._type == ParameterType.Empty and self.param_has_default() and isinstance(self.param_get_default(), bool):
            # Type set implicitly via the default value
            return True
        return False

    def param_has_default(self) -> bool:
        """Return True if the parameter has a default value."""
        from .parameter import Parameter
        if self._default_value is Parameter.Empty:
            return False
        return True

    def param_get_default(self) -> Any:
        """Return the default value of the parameter. Raise if there was no default value specified."""
        assert self.param_has_default()
        return self._default_value

    def is_list(self) -> bool:
        """Return True if the parameter type is a list."""
        if self.is_union():
            return False

        annotation = self._type
        if get_origin(annotation) is list:
            return True
        if annotation is list:
            return True

        return False

    def get_the_list_type(self) -> Any:
        """Return the type of the list, or raise if not a list.

        If the annotation is a list or list[X], it simpl returns that.
        If the type is a list[x]|None, it returns the list part from that union.
        """
        if self.is_list():
            return self._type
        elif self.is_union_list_none():
            return self.get_list_from_union()
        else:
            msg = "Not a list"
            raise Exception(msg)

    def list_has_type_args(self) -> bool:
        """Can be called on x:list nad x:list|None."""
        listtype = self.get_the_list_type()

        list_arg_types = get_args(listtype)

        if list_arg_types is None:
            return False

        if len(list_arg_types) == 1:
            return True

        return False

    def get_list_from_union(self) -> Any:
        """Return the list type from a union of list and None."""
        assert self.is_union_list_none()
        union_args = get_args(self._type)
        assert len(union_args) == 2
        for arg in union_args:
            if get_origin(arg) is list:
                return arg

    def get_list_type_args(self) -> None | Any:
        """Return the type arguments of the list annotation, or None if there are none."""
        listtypevar = self.get_the_list_type()

        list_arg_types = get_args(listtypevar)
        if list_arg_types is None:
            return None
        assert isinstance(list_arg_types, tuple)
        if len(list_arg_types) == 0:
            return None
        assert len(list_arg_types) == 1, f"list_arg_types: {list_arg_types}"
        return list_arg_types[0]
