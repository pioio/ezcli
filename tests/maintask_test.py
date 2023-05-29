# Here we run tests that ensure that misuing the api results in errors
from unittest import TestCase
import unittest
from unittest.mock import patch


import taskcli
import inspect

from taskcli import cli, task, arg
from taskcli.taskcli import mock_decorator
from taskcli.taskcli import Task


class TaskCLITestCase(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()


class TestTaskMain(TaskCLITestCase):
    def test_main_task_works(self):
        @task(main=True)
        def fun():
            return 1

        taskcli.cli(argv="foo".split(" "), force=True)

    def test_conflicts(self):
        # if we have a default function with a (unnamed) argument
        # and also other tasks, it's unclear if we're calling the default function
        # or trying to call a different task.
        # ./script foobar  # is this calling the default function with argument "foobar", or calling the task "foobar"?
        # to avoid ambiguity, we raise an error

        @task(main=True)
        @arg("my_arg")  # mandatory argument
        def fun(my_arg):
            return "fun_was_called"

        @task
        def foobar():
            return "foobar"

        with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
            with self.assertRaisesRegex(Exception, "The default task"):
                taskcli.cli(argv="foo foobar".split(" "), force=True)

    def test_if_there_only_one_task_make_it_main(self):
        @task
        def fun():
            return 1

        taskcli.cli(argv="foo".split(" "), force=True)

    def test_implicit_default_task_works(self):
        @task
        def fun():
            return 1

        with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
            with self.assertRaisesRegex(Exception, "No task name provided, and there's no default task"):
                taskcli.cli(argv="foo".split(" "), force=True, explicit_default_task=True)


class TestTaskClass(TaskCLITestCase):
    def test_task_class(self):
        @task
        @arg("a", type=int)
        def fun(a):
            return a

        atask = taskcli.taskcli.tasks["fun"]
        self.assertEqual(atask.has_positional_args(), True)

    def test_task_class2(self):
        @task
        def fun(a):
            return a

        atask = taskcli.taskcli.tasks["fun"]
        self.assertEqual(atask.has_positional_args(), False)
