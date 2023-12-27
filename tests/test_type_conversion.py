import os
import subprocess

import pytest

import taskcli
from taskcli import dispatch, task
import taskcli.core
from taskcli.group import Group
from taskcli.parser import _extract_extra_args
from taskcli.task import Task
from taskcli.taskcli import TaskCLI

from .tools import reset_context_before_each_test
from  . import tools

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
def test_conversion_to_float_raises_(value):
    @task
    def foo(a: float):
        assert isinstance(a, float)

    tools.include_tasks()
    with pytest.raises(Exception, match="could not convert string to float"):
        dispatch(["foo", value])


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
