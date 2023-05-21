# here we test only params, not args
from unittest import TestCase
import unittest

import taskcli
import inspect

from taskcli import cli, task, arg
from taskcli.taskcli import mock_decorator

class TaskCLITestCase(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()




class TestTaskCliParamOptions(TaskCLITestCase):
    def test_simplest_no_params(self):
        @task
        def fun():
            return 1
        ret = cli(argv=["foo", "fun"] , force=True)
        self.assertEqual(ret, 1)

        with self.assertRaisesRegex(Exception, "unrecognized arguments:"):
            cli(argv=["foo", "fun", "123"] , force=True)

    def test_simple(self):
        @task
        def fun(a, b):
            assert isinstance(a, str)
            assert isinstance(b, str)
            return a + b

        ret = cli(argv=["foo", "fun", "1", "2"] , force=True)
        self.assertEqual(ret, "12")

        with self.assertRaisesRegex(Exception, "unrecognized arguments: 3"):
            cli(argv=["foo", "fun", "1", "2", "3"] , force=True)

    def test_simple2(self):
        @task
        def fun2(a:int,b:int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return a + b

        ret = cli(argv=["foo", "fun2", "1", "2"], force=True)
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
            cli(argv=["foo", "fun", "123"] , force=True)

        with self.assertRaisesRegex(Exception, "argument --aa: expected one argument"):
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
            cli(argv=["foo", "fun", "123"] , force=True)

        with self.assertRaisesRegex(Exception, "argument -a: expected one argument"):
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
            assert isinstance(a, list)
            if len(a) > 0:
                assert isinstance(a[0], int)
            return a

        argv = ["foo", "fun", "1", "2", "3"]
        ret = taskcli.cli(argv=argv, force=True)
        self.assertListEqual(ret, [1,2,3])

        argv = ["foo", "fun", "1", "2", "3", "4"]
        ret = taskcli.cli(argv=argv, force=True)
        self.assertListEqual(ret, [1,2,3,4])

        argv = ["foo", "fun"]
        ret = taskcli.cli(argv=argv, force=True)
        self.assertListEqual(ret, [])


    def test_simple_list_with_defaults_fails(self):
        with self.assertRaisesRegex(Exception, "Function params .* of type 'list' must not"):
            @task
            def fun(aaaa:list[int]=[]):
                assert isinstance(aaaa, list)
                assert len(aaaa) == 0
                return aaaa


