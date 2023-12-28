from typing import Annotated

from taskcli import arg
from taskcli.parameter import Parameter
from taskcli.task import Task


def test_basic():
    def foo(x):
        pass

    task = Task(foo)
    param = task.params[0]
    assert param.name == "x"
    assert param.type == Parameter.Empty


def test_basic_types_from_signature():
    def foo(x: str) -> None:
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == Parameter.Empty
    assert not param.has_default()


def test_basic_types_from_annotated():
    def foo(x: Annotated[str, None]) -> None:
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == Parameter.Empty
    assert not param.has_default()


def test_basic_default_from_param():
    def foo(x: str = "foobar") -> None:
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == "foobar"
    assert param.has_default()


def test_basic_default_from_annotated():
    xxx = arg(str, default="from-annotated")

    def foo(x: xxx):  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == "from-annotated"
    assert param.has_default()


def test_basic_default_from_param_and_annotated():
    xxx = arg(str, default="from-annotated")

    def foo(
        x: xxx,  # type: ignore # noqa: PGH003
        y: xxx = "from-signature",  # type: ignore # noqa: PGH003
    ) -> None:
        pass

    task = Task(foo)
    param1 = task.params[0]
    param2 = task.params[1]

    assert param1.name == "x"
    assert param1.type == str
    assert param1.default == "from-annotated"
    assert param1.has_default()

    assert param2.name == "y"
    assert param2.type == str
    assert param2.default == "from-signature"
    assert param2.has_default()


def test_basic_no_default_but_annotated():
    xxx = arg(str)

    def foo(x: xxx) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == Parameter.Empty
    assert not param.has_default()


def test_list_type_1():
    def foo(x: list) -> None:
        pass
    param = Task(foo).params[0]
    assert param.is_list()
    assert not param.is_union_list_none()
    assert not param.has_default()
    assert not param.is_bool()

def test_list_type_2():
    def foo(x: list=[]) -> None:
        pass
    param = Task(foo).params[0]
    assert param.is_list()
    assert not param.is_union_list_none()
    assert param.has_default()
    assert not param.list_has_type_args()


def test_list_type_3():
    def foo(x: list[int]) -> None:
        pass
    param = Task(foo).params[0]
    assert param.is_list()
    assert not param.is_union_list_none()
    assert not param.has_default()
    assert param.list_has_type_args()
    assert param.get_list_type_args() == int

def test_list_type_4():
    def foo(x: list[int]=[]) -> None:
        pass
    param = Task(foo).params[0]
    assert param.is_list()
    assert not param.is_union_list_none()
    assert param.has_default()
    assert param.get_list_type_args() == int



def test_union_list_none1():
    def foo(x: list|None) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.is_list()
    assert param.is_union_list_none()

from typing import get_origin, get_args

def test_union_list_none2():
    def foo(x: list[int]|None) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.is_list()
    #print (get_args(param.type))
    assert param.is_union_list_none()


def test_union_list_none3():
    def foo2(x: list|None|dict) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo2).params[0]
    assert not param.is_list()
    assert not param.is_union_list_none()



def test_is_bool_explicit():
    def foo(x: bool) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.is_list()
    assert param.is_bool()
    assert not param.is_union_list_none()


def test_is_bool2_implicit():
    def foo(x=False) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.is_list()
    assert param.is_bool()
    assert not param.is_union_list_none()

def test_is_bool2_explicit_with_default():
    def foo(x:bool=False) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.is_list()
    assert param.is_bool()
    assert not param.is_union_list_none()
