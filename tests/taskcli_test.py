from unittest import TestCase
import unittest
from unittest.mock import patch

import taskcli
import inspect

from taskcli import cli, task, arg
from taskcli.taskcli import mock_decorator


class TaskCLITestCase(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()


class TestTaskcli(TaskCLITestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()

    def test_fun_rerunning_cli_works(self):
        @task
        @arg("a", type=int, nargs="+")
        def fun(a: list[int]):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        argv = ["foo", "fun", "1", "2", "3"]
        cli(argv=argv, force=True)
        cli(argv=argv, force=True)

    def test_analyze_signature(self):
        def fun(a, b, c):
            pass

        data = taskcli.taskcli.analyze_signature(fun)
        self.assertEqual(data["func_name"], "fun")
        self.assertEqual(data["module"], __name__)
        self.assertEqual(data["params"]["a"]["param_name"], "a")
        self.assertEqual(data["params"]["b"]["param_name"], "b")
        self.assertEqual(data["params"]["c"]["param_name"], "c")
        self.assertEqual(data["params"]["a"]["type"], inspect._empty)

    def test_analyze_with_types(self):
        def fun(a: int, b, c):
            pass

        data = taskcli.taskcli.analyze_signature(fun)

        self.assertEqual(data["func_name"], "fun")
        self.assertEqual(data["params"]["a"]["type"], int)


class TestTaskCliCalls(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()

    def test_simple3_mixed_definitions_raises_on_dup(self):
        with self.assertRaisesRegex(Exception, "Duplicate arg decorator for 'a' in fun3"):

            @task
            @arg("a", type=int)
            @arg("a", type=int)
            def fun3(a, b: int):
                assert isinstance(a, int)
                assert isinstance(b, int)
                return a + b

    def test_simple3_mixed_definitions(self):
        @task
        @arg("a", type=int)
        def fun3(a, b: int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return a + b

        ret = cli(argv="foo fun3 1 -b 2".split(), force=True)
        self.assertEqual(ret, 3)


class TestTaskCliArgOptions(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()

    def test_arg_options(self):
        @task
        @arg("--aa", type=int)
        def fun(aa):
            assert isinstance(aa, int)
            return aa

        ret = cli(argv=["foo", "fun", "--aa", "1"], force=True)
        self.assertEqual(ret, 1)

    def test_arg_options_only_short(self):
        @task
        @arg("-a", type=int)
        def fun(a):
            assert isinstance(a, int), f"Expected int, got {type(a)}"
            return a

        ret = cli(argv=["foo", "fun", "-a", "1"], force=True)
        self.assertEqual(ret, 1)

    def test_arg_options_long_short(self):
        @task
        @arg("--aa", "-a", "--aaa", type=int)
        def fun(aa):
            assert isinstance(aa, int)
            return aa

        ret = cli(argv=["foo", "fun", "--aa", "1"], force=True)
        self.assertEqual(ret, 1)

        ret = cli(argv=["foo", "fun", "-a", "1"], force=True)
        self.assertEqual(ret, 1)

        ret = cli(argv=["foo", "fun", "--aaa", "1"], force=True)
        self.assertEqual(ret, 1)

        # ret = cli(argv=["foo", "fun", "0"], force=True)
        # self.assertEqual(ret, False)


class TestTaskCliCallsLists(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()
        # print("------------")

    def test_simple_list_with_arg(self):
        @task
        @arg("a", type=int, nargs="+")
        def fun(a):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        ret = cli(argv=["foo", "fun", "1", "2", "3"], force=True)
        self.assertListEqual(ret, [1, 2, 3])

    def test_simple_list_with_arg2(self):
        @task
        @arg("a", type=int, nargs=3)
        def fun(a):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        ret = cli(argv=["foo", "fun", "1", "2", "3"], force=True)
        self.assertListEqual(ret, [1, 2, 3])

    def test_simple_list_with_arg_raises_on_nargs_mismatch(self):
        @task
        @arg("a", type=int, nargs=3)
        def fun(a):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        argv = ["foo", "fun", "1"]
        argv = argv[2:]  # since we're using build_parser_for_task directly, we need to remove the first two elements
        parser = taskcli.taskcli.build_parser_for_task(task_name="fun", exit_on_error=False)
        from taskcli.taskcli import ParsingError

        with self.assertRaisesRegex(ParsingError, "the following arguments are required: a"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                taskcli.taskcli.parse(parser, argv)


class TestCallingOtherTasks(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()
        # print("------------")

    def test_calling_other_tasks(self):
        @task
        def fun(a):
            return a

        @task
        def fun2(a):
            return fun(a)

        ret = cli(argv=["foo", "fun2", "-a", "1"], force=True)
        self.assertEqual(ret, "1")

    def test_basic_conversion_works(self):
        @task
        @arg("a", type=int)
        def fun(a):  # should convert string to int
            assert isinstance(a, int)
            return a

        ret = cli(argv=["foo", "fun", "1"], force=True)
        self.assertEqual(ret, 1)

    def test_basic_conversion_works_errors_out(self):
        @task
        @arg("a", type=int)
        def fun(a):  # should convert string to int
            assert isinstance(a, int)
            return a

        with self.assertRaisesRegex(Exception, "argument a: invalid int value: 'xxxx'"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                ret = cli(argv=["foo", "fun", "xxxx"], force=True)

    @unittest.skip("Not implemented yet - likely a lot of work")
    def test_calling_other_tasks_with_type_conversion(self):
        # For this to work, we need to do some additional type conversion magic
        # in fun2 its argparse doing the conversion in cli(), but in 'fun' it's not.
        # that addiitonal conversion needs to be done in the task decorator
        @task
        @arg("a", type=int)
        def fun(a):  # should convert string to int
            assert isinstance(a, int)
            return a

        @task
        @arg("b", type=str)
        def fun2(b):
            assert isinstance(b, str)
            return fun(b)

        ret = cli(argv=["foo", "fun2", "1"], force=True)
        self.assertEqual(ret, 1)


# TODO arg decorators with --foo
# TODO check for _ in arg decorators
