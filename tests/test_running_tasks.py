"""Tests that actually run external tasks script to test everything end to end."""
import os
import subprocess

import pytest

from . import tools


def test_groups_are_listed():
    with tools.simple_list_format():
        stdout, stderr = tools.run_tasks("tests/fixtures/groups.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "# default",
        "task4",
        "",
        "# foobar",
        "task1",
        "task2",
        "task3",
    ]


def test_sort_important():
    with tools.simple_list_format():
        stdout, stderr = tools.run_tasks("tests/fixtures/sort_important.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "# default",
        "task2",  # marked as important
        "task1",
        "task3",
        "task4",
    ]


@pytest.mark.parametrize(
    "args",
    [
        ["task1", "foo", "foo"],
        ["task2", "arg1 arg2", "arg1 arg2"],
        ["task3", "arg1 --arg2=arg2", "arg1 arg2"],
        ["task4", "arg1 --arg2=444", "arg1 444"],
        ["task5", "4.4 --arg2=444", "4.4 444"],
        ["task-list1-a", "--arg1 1 1", """[1.0, 1.0]"""],
        ["task-list1-a-default", "", """[1.0]"""],  # should also be converted from 1 to 1.0
        ["task-list1-b", "1 1", """[1.0, 1.0]"""],
        ["task-list1-b-default", "", """[444.0]"""],
        ["task-list1-c", "1 xx", """['1', 'xx']"""],
        ["task-list1-c-default", "", """['def1', 'def2']"""],  # should use default value
        ["task-bool1", "--arg1", "True"],
        ["task-bool2", "--arg1 --arg2 44", "True 44"],
        ["task-complex1", "11 --arg3 --arg4 44", "11 3.0 True 44"],  # using optional positional arg
        ["task-complex1", "11 42.1 --arg3 --arg4 44", "11 42.1 True 44"],  # Specify optional positional arg
    ],
)
def test_arguments(args):
    task_name, args, expected_output = args

    with tools.simple_list_format():
        stdout, stderr = tools.run_tasks(f"./tests/fixtures/arguments.py {task_name} {args}")

    print("expected_output", expected_output)
    print("stdout", stdout)
    print("stderr", stderr)
    assert stdout.strip() == expected_output


@pytest.mark.parametrize(
    "args",
    [
        ["task-bool1-error", "", "Either make the boolean parameter explicitly a keyword-only "],
    ],
)
def test_invalid_arguments(args):
    task_name, args, expected_output = args

    with tools.simple_list_format():
        stdout, stderr = tools.run_tasks(f"./tests/fixtures/arguments.py {task_name} {args}")

    print("expected_output", expected_output)
    print("stdout", stdout)
    print("stderr", stderr)
    assert expected_output in stderr.strip()
