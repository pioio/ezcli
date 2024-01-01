import os
import subprocess

import pytest

import taskcli
import taskcli.core
from taskcli.dispatching import dispatch
from taskcli import task, tt
from taskcli.group import Group
from taskcli.dispatching import extract_extra_args
from taskcli.task import Task
from taskcli.taskcli import TaskCLI

from . import tools
from .tools import reset_context_before_each_test


@pytest.mark.parametrize("value", ["1", "-12", "0", "-0"])
def test_conversion_to_int_works(value):
    @task
    def foo(a: int):
        assert isinstance(a, int)

    tools.include_tasks()
    dispatch(["foo", value])


@pytest.mark.parametrize("value", ["1", "1.9", "0", "-1", "-0.9", "23234234.23234234243"])
def test_conversion_to_float_works(value):
    @task
    def foo(a: float):
        assert isinstance(a, float)

    tools.include_tasks()
    dispatch(["foo", value])


@pytest.mark.parametrize("value", ["foobar"])
def test_conversion_to_float_raises_(value, capsys):
    @task
    def foo(a: float):
        assert isinstance(a, float)

    tools.include_tasks()
    with pytest.raises(SystemExit, match="2"):
        dispatch(["foo", value])

    assert "invalid float value" in capsys.readouterr().err


@pytest.mark.skip()
@pytest.mark.parametrize("values", [["1"]])
def test_conversion_to_list_of_ints(values):
    @task
    def foo(args: list[int]):
        for element in args:
            assert isinstance(element, int), f"Expected int, got {type(element)}"

    tools.include_tasks()

    dispatch(["foo", *values])


# @pytest.mark.parametrize("value", ["1", "1.9", "0", "-1", "-0.9", "23234234.23234234243"])
@pytest.mark.skip("TODO: disallow positional bool? or expect it to be a string?")
def test_conversion_to_bool_works():
    @task
    def foo(a: bool):
        assert isinstance(a, bool)

    tools.include_tasks()
    dispatch(["foo", "true"])


def test_custom_user_type():
    class Foobar:
        def __init__(self, value):
            self.value = value

    FoobarType = tt.arg(Foobar, type=Foobar)

    @task
    def foo(a: FoobarType):
        assert isinstance(a, Foobar)
        return a

    t = tools.include_task()
    ret = t.dispatch(["somearg"])
    assert isinstance(ret, Foobar)
    assert ret.value == "somearg"


def test_custom_user_coversion_function():
    def convert(value: str):
        return "converted-" + value

    FoobarType = tt.arg(str, type=convert)

    @task
    def foo(a: FoobarType):
        assert isinstance(a, str)
        return a

    t = tools.include_task()
    assert t.dispatch(["somearg"]) == "converted-somearg"


def test_aliases_work():
    @task(aliases="foo1")
    def task1():
        return "t1"

    @task(aliases=["foo2a", "foo2b"])
    def task2():
        return "t2"

    tasks = tools.include_tasks()

    assert dispatch(["task1"]) == "t1"
    assert dispatch(["foo1"]) == "t1"
    assert dispatch(["task2"]) == "t2"
    assert dispatch(["foo2a"]) == "t2"
    assert dispatch(["foo2b"]) == "t2"
