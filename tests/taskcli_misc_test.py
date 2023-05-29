# Here we run tests that ensure that misuing the api results in errors
from unittest import TestCase
import unittest

import taskcli
import inspect

from taskcli import cli, task, arg
from taskcli.taskcli import mock_decorator


class TaskCLITestCase(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()


class TestTaskCliWeirdDecoratorOrder(TaskCLITestCase):
    def test_decorators_work_when_task_is_added_last(self):
        @arg("a", type=int)
        @task
        def fun3(a, b: int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return a + b

        argv = "./foo fun3 1 -b 2".split()
        ret = cli(argv=argv, force=True)
        self.assertEqual(ret, 3)

    def test_decorators_work_when_task_is_in_between(self):
        @arg("a", type=int)
        @task
        @arg("b", type=int)
        def fun3(a, b):
            return a + b

        ret = cli(argv=["foo", "fun3", "1", "2"], force=True)
        self.assertEqual(ret, 3)

    def test_decorators_work_with_third_party_decorators(self):
        @mock_decorator()
        @arg("a", type=int)
        @mock_decorator()
        @task
        @mock_decorator()
        @arg("b", type=int)
        @mock_decorator()
        def fun3(a, b):
            return a + b

        ret = cli(argv=["foo", "fun3", "1", "2"], force=True)
        self.assertEqual(ret, 3)
