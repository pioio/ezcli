from typing import Annotated, get_args, get_origin
from .tools import reset_context_before_each_test
from . import tools
from taskcli import arg
from taskcli.parameter import Parameter
from taskcli.parametertype import ParameterType
from taskcli.task import Task


def test_basic():
    def foo(x):
        pass

    task = Task(foo)
    param = task.params[0]
    assert param.name == "x"
    assert param.type.raw == ParameterType.Empty


def test_basic_types_from_signature():
    def foo(x: str) -> None:
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type.raw == str
    assert param.default == Parameter.Empty
    assert not param.has_default()


def test_basic_types_from_annotated():
    def foo(x: Annotated[str, None]) -> None:
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type.raw == str
    assert param.default == Parameter.Empty
    assert not param.has_default()


def test_basic_default_from_param():
    def foo(x: str = "foobar") -> None:
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type.raw == str
    assert param.default == "foobar"
    assert param.has_default()


def test_basic_default_from_annotated():
    xxx = arg(str, default="from-annotated")

    def foo(x: xxx):  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type.raw == str
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
    assert param1.type.raw == str
    assert param1.default == "from-annotated"
    assert param1.has_default()

    assert param2.name == "y"
    assert param2.type.raw == str
    assert param2.default == "from-signature"
    assert param2.has_default()


def test_basic_no_default_but_annotated():
    xxx = arg(str)

    def foo(x: xxx) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type.raw == str
    assert param.default == Parameter.Empty
    assert not param.has_default()


def test_list_type_1():
    def foo(x: list) -> None:
        pass

    param = Task(foo).params[0]
    assert param.type.is_list()
    assert not param.type.is_union_list_none()
    assert not param.has_default()
    assert not param.type.is_bool()


def test_list_type_2():
    def foo(x: list = []) -> None:  # noqa: B006
        pass

    param = Task(foo).params[0]
    assert param.type.is_list()
    assert not param.type.is_union_list_none()
    assert param.has_default()
    assert not param.type.list_has_type_args()


def test_list_type_3():
    def foo(x: list[int]) -> None:
        pass

    param = Task(foo).params[0]
    assert param.type.is_list()
    assert not param.type.is_union_list_none()
    assert not param.has_default()
    assert param.type.list_has_type_args()
    assert param.type.get_list_type_args() == int


def test_list_type_4():
    def foo(x: list[int] = []) -> None:  # noqa: B006
        pass

    param = Task(foo).params[0]
    assert param.type.is_list()
    assert not param.type.is_union_list_none()
    assert param.has_default()
    assert param.type.get_list_type_args() == int


def test_union_list_none1():
    def foo(x: list | None) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.type.is_list()
    assert param.type.is_union_list_none()


def test_union_list_none2():
    def foo(x: list[int] | None) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.type.is_list()
    assert param.type.is_union_list_none()


def test_union_list_none3():
    def foo2(x: list | None | dict) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo2).params[0]
    assert not param.type.is_list()
    assert not param.type.is_union_list_none()


def test_is_bool_explicit():
    def foo(x: bool) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.type.is_list()
    assert param.type.is_bool()
    assert not param.type.is_union_list_none()


def test_is_bool2_implicit():
    def foo(x=False) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.type.is_list()
    assert param.type.is_bool()
    assert not param.type.is_union_list_none()


def test_is_bool2_explicit_with_default():
    def foo(x: bool = False) -> None:  # type: ignore # noqa: PGH003
        pass

    param = Task(foo).params[0]
    assert not param.type.is_list()
    assert param.type.is_bool()
    assert not param.type.is_union_list_none()

from taskcli import task, tt
from typing import Any


def test_3_ways_of_passing_short_options():
    @task
    def foo(*, param:int=0) -> int:
        return param

    t = tt.get_tasks()[0]

    assert t.dispatch(["--param", "1"]) == 1
    assert t.dispatch(["--param=1"]) == 1

    assert t.dispatch(["-p", "1"]) == 1
    assert t.dispatch(["-p=1"]) == 1
    assert t.dispatch(["-p1"]) == 1

    assert t.dispatch(["-p1", "-p2"]) == 2, "Second one should take precedence"



def test_automatic_short_param_names_work():
    @task
    def foo(*, param0:int=0, param1:int=0, param2:int=0, foobar3:str="0", foobar4:str="0", bake:bool=False) -> list[Any]:
        return [param0, param1, param2, foobar3, foobar4, bake]

    t = tt.get_tasks()[0]

    res = t.dispatch(["--param0", "1", "--param1", "1", "--param2", "1", "--foobar3", "1", "--foobar4", "1"])
    assert res == [1, 1, 1, "1", "1", False]

    res = t.dispatch(["-p1"])
    assert res == [1, 0, 0, "0", "0", False]

    res = t.dispatch(["-p", "1"])
    assert res == [1, 0, 0, "0", "0", False]

    res = t.dispatch(["-p=1"])
    assert res == [1, 0, 0, "0", "0", False]

    res = t.dispatch(["-P1"])
    assert res == [0, 1, 0, "0", "0", False]

    res = t.dispatch(["-P1", "-F1"])
    assert res == [0, 1, 0, "0", "1", False]

    res = t.dispatch(["-P1", "-b", "-p2"])
    assert res == [2, 1, 0, "0", "0", True]
