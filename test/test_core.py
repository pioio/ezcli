import taskcli.core

import unittest
from unittest import TestCase

# from taskcli.core import Task
from taskcli import Task


class TestTaskcli(TestCase):
    def test_construction_simple(self):
        def fun():
            pass

        task = Task(fun)
        self.assertEqual(task.name, "fun")
        self.assertEqual(task.func, fun)
        self.assertEqual(task.arguments, [])

    def test_construction_simple_with_args(self):
        def fun(arg1, arg2="foobar", arg3: int = 42, arg4=False):
            pass

        task = Task(fun)
        self.assertEqual(task.name, "fun")
        self.assertEqual(task.func, fun)
        self.assertEqual(len(task.arguments), 4)

        arg = task.arguments[0]
        self.assertEqual(arg.name, "arg1")
        self.assertEqual(arg.default, None)
        self.assertEqual(arg.type, None)

        arg = task.arguments[1]
        self.assertEqual(arg.name, "arg2")
        self.assertEqual(arg.default, "foobar")
        self.assertEqual(arg.type, str)

        arg = task.arguments[2]
        self.assertEqual(arg.name, "arg3")
        self.assertEqual(arg.default, 42)
        self.assertEqual(arg.type, int)

        arg = task.arguments[3]
        self.assertEqual(arg.name, "arg4")
        self.assertEqual(arg.default, False)
        self.assertEqual(arg.type, bool)


class TestCore(TestCase):
    def test_basic_case(self):
        self.assertEqual(1, 1)
