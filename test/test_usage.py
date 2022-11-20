import taskcli.usage

import unittest
from unittest import TestCase

from taskcli.usage import (
    get_line_for_argument,
    get_flags_for_argument,
    get_usage_for_task,
    get_line_task_name,
)

from taskcli.core import Argument, Task


class TestTaskcli(TestCase):
    def test_arg_line(self):

        arg = Argument("foobar", default=42, type=int)
        self.assertEqual(arg.long_cli_flag, "--foobar")
        self.assertEqual(arg.short_cli_flag, None)

        line = get_line_for_argument(arg)
        self.assertEqual(line, "[--foobar]           Default: 42")

        arg = Argument("foobar", default=None, type=int)
        line = get_line_for_argument(arg)
        self.assertEqual(line, " --foobar            ")

    def test_get_flags_for_argument(self):
        arg = Argument("foobar", default=42, type=int)
        flags = get_flags_for_argument(arg)
        self.assertEqual(flags, "--foobar")

        arg = Argument("f", default=42, type=int)
        flags = get_flags_for_argument(arg)
        self.assertEqual(flags, "-f")

        arg = Argument("foobar", default=42, type=int, short_cli_flag="-x")
        flags = get_flags_for_argument(arg)
        self.assertEqual(flags, "-x|--foobar")

    def test_get_line_task_name(self):
        def foobar(x: int):
            """My docstring
            Line 2 of docstring"""
            pass

        task = Task(foobar)
        line = get_line_task_name(task)
        self.assertEqual(line, "foobar               My docstring")


class TestUsageTask(TestCase):
    def test_basic_case(self):
        def foobar():
            """My docstring"""
            pass

        task = Task(foobar)
        lines = get_usage_for_task(task)
