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



class TestTaskMisuse(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()
        #print("------------")

    def test_two_task_decorators_fail(self):
        with self.assertRaisesRegex(Exception, "Duplicate @task decorator"):
            @task
            @task
            def fun():
                pass

    # Here, because order of decorators is not enforced, we can check only when running cli()
    # def test_arg_task_required(self):
    #     with self.assertRaisesRegex(Exception, "Duplicate @task decorator"):
    #         @arg("a", type=int)
    #         def fun():
    #             pass


    def test_arg_with_no_matching_param_fails(self):
        with self.assertRaisesRegex(Exception, "arg decorator for 'a' in function 'fun' does not match any param in the function signature"):
            @task
            @arg("a", type=int)
            def fun():
                pass

    def test_duplicate_args_fails(self):
        with self.assertRaisesRegex(Exception, "Duplicate arg decorator for 'a' in fun"):
            @task
            @arg("a", type=int)
            @arg("a", type=int)
            def fun(a):
                pass


    def test_basic(self):
        @task
        @arg("--option-a", type=int, nargs=2)
        def fun(option_a, pos_a):
            assert isinstance(option_a, list)
            assert isinstance(option_a[0], int)
            assert isinstance(pos_a, str)
            return option_a, pos_a

        argv = "./foo fun --pos-a xxx_pos_a --option-a 1 42".split()
        a, b = cli(argv=argv, force=True)

        self.assertEqual(a, [1,42])
        self.assertEqual(b, "xxx_pos_a")
