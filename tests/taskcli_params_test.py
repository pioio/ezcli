# here we test only params, not args
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


class TestTaskCliParamOptions(TaskCLITestCase):
    def test_prints_error_if_not_need_arg_specified_when_none_expected(self):
        @task
        def fun():
            return 1
        ret = cli(argv=["foo", "fun"] , force=True)
        self.assertEqual(ret, 1)

        with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
            with self.assertRaisesRegex(Exception, "unrecognized arguments:"):
                cli(argv=["foo", "fun", "123"] , force=True)

    def test_params_with_no_default_are_required(self):
        @task
        def fun(a):
            return a

        with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
            with self.assertRaisesRegex(Exception, "the following arguments are required: -a"):
                cli(argv=["foo", "fun"] , force=True)


    def test_prints_error_if_not_need_arg_specified_when_two_expected(self):
        @task
        def fun(a, b):
            assert isinstance(a, str)
            assert isinstance(b, str)
            return a + b

        argv = "./foo fun -a 1 -b 2".split()
        ret = cli(argv=argv, force=True)
        self.assertEqual(ret, "12")

        with self.assertRaisesRegex(Exception, "unrecognized arguments: 3"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                argv = "./foo fun -a 1 -b 2 3".split()
                cli(argv=argv , force=True)


    def test_simple_but_long_name(self):
        @task
        def fun_fun(a, b):
            assert isinstance(a, str)
            assert isinstance(b, str)
            return a + b

        ret = cli(argv="foo fun_fun -a 1 -b 2".split() , force=True)
        self.assertEqual(ret, "12")

    def test_simple2(self):
        @task
        def fun2(a:int,b:int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return a + b

        ret = cli(argv="foo fun2 -a 1 -b 2".split(), force=True)
        self.assertEqual(ret, 3)

    def test_param_options(self):
        DEFAULT=3
        @task
        def fun(aa:int=DEFAULT):
            assert isinstance(aa, int)
            return aa

        ret = cli(argv=["foo", "fun", "--aa", "1"], force=True)
        self.assertEqual(ret, 1)

        ret = cli(argv=["foo", "fun"], force=True)
        self.assertEqual(ret, DEFAULT)

        with self.assertRaisesRegex(Exception, "unrecognized arguments:"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                cli(argv=["foo", "fun", "123"] , force=True)

        with self.assertRaisesRegex(Exception, "argument --aa: expected one argument"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                cli(argv=["foo", "fun", "--aa"] , force=True)


    def test_param_options_only_short(self):
        DEFAULT=3
        @task
        def fun(a:int=DEFAULT):
            assert isinstance(a, int)
            return a

        ret = cli(argv=["foo", "fun", "-a", "1"], force=True)
        self.assertEqual(ret, 1)

        ret = cli(argv=["foo", "fun"], force=True)
        self.assertEqual(ret, 3)

        with self.assertRaisesRegex(Exception, "unrecognized arguments:"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                cli(argv=["foo", "fun", "123"] , force=True)

        with self.assertRaisesRegex(Exception, "argument -a: expected one argument"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                cli(argv=["foo", "fun", "-a"] , force=True)




class TestTaskCliParamsBools(TaskCLITestCase):
    def test_bool_basic_False(self):
        @task
        def fun(a:bool=False):
            assert isinstance(a, bool)
            return a

        ret = cli(argv=["foo", "fun", "-a"], force=True)
        self.assertEqual(ret, True)

        ret = cli(argv=["foo", "fun"], force=True)
        self.assertEqual(ret, False)

    def test_bool_basic_True(self):
        @task
        def fun(a:bool=True):
            assert isinstance(a, bool)
            return a

        ret = cli(argv=["foo", "fun", "-a"], force=True)
        self.assertEqual(ret, False)

        ret = cli(argv=["foo", "fun"], force=True)
        self.assertEqual(ret, True)

    def test_bool_raises_with_no_default_value(self):
        # with no default value they end up being positional args, which are always true unless empty string
        with self.assertRaisesRegex(Exception, "bool params must"):
            @task
            def fun(a:bool):
                assert isinstance(a, int)
                return a



class TestTaskCliParamsLists(TaskCLITestCase):
    def test_simple_list_without_arg(self):
        @task
        def fun(a:list[int]):
            assert isinstance(a, list), f"expected list[int] got {type(a)}"
            if len(a) > 0:
                assert isinstance(a[0], int), f"got {type(a[0])}"
            return a


        argv = "foo fun -a 1 2 3".split()
        ret = taskcli.cli(argv=argv, force=True)
        self.assertListEqual(ret, [1,2,3])

        argv = "foo fun -a 1 2 3 4".split()
        ret = taskcli.cli(argv=argv, force=True)
        self.assertListEqual(ret, [1,2,3,4])


        with self.assertRaisesRegex(Exception, "the following arguments are required: -a"):
            with patch("taskcli.taskcli.ArgumentParser.print_help") as ph:
                argv = "foo fun".split()
                ret = taskcli.cli(argv=argv, force=True)


    def test_simple_list_with_defaults_fails(self):
        with self.assertRaisesRegex(Exception, "Function params .* of type 'list' must not"):
            @task
            def fun(aaaa:list[int]=[]):
                assert isinstance(aaaa, list)
                assert len(aaaa) == 0
                return aaaa


