from unittest import TestCase
import unittest

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
        def fun(a:list[int]):
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
        self.assertEqual(data['func_name'], 'fun')
        self.assertEqual(data['module'], __name__)
        self.assertEqual(data['params']['a']['param_name'], 'a')
        self.assertEqual(data['params']['b']['param_name'], 'b')
        self.assertEqual(data['params']['c']['param_name'], 'c')
        self.assertEqual(data['params']['a']['type'], inspect._empty)

    def test_analyze_with_types(self):
        def fun(a:int, b, c):
            pass

        data = taskcli.taskcli.analyze_signature(fun)

        self.assertEqual(data['func_name'], 'fun')
        self.assertEqual(data['params']['a']['type'], int)


class TestTaskCliCalls(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()

    def test_simple(self):
        @task
        def fun(a, b):
            assert isinstance(a, str)
            assert isinstance(b, str)
            return 1

        ret = cli(argv=["foo", "fun", "1", "2"] , force=True)
        self.assertEqual(ret, 1)

    def test_simple2(self):
        @task
        def fun2(a:int,b:int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return a + b

        ret = cli(argv=["foo", "fun2", "1", "2"], force=True)
        self.assertEqual(ret, 3)

    def test_simple3_mixed_definitions_raises_on_dup(self):
        with self.assertRaisesRegex(Exception, "Duplicate arg decorator for 'a' in fun3"):
            @task
            @arg("a", type=int)
            @arg("a", type=int)
            def fun3(a,b:int):
                assert isinstance(a, int)
                assert isinstance(b, int)
                return a + b

    def test_simple3_mixed_definitions(self):
        @task
        @arg("a", type=int)
        def fun3(a,b:int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return a + b

        ret = cli(argv=["foo", "fun3", "1", "2"], force=True)
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
            assert isinstance(a, int)
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


class TestTaskCliParamOptions(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()


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

class TestTaskCliBools(TaskCLITestCase):
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


        # ret = cli(argv=["foo", "fun", "0"], force=True)
        # self.assertEqual(ret, False)



class TestTaskCliDecoratorOrder(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()
        print("------------")

    def test_simple3_mixed_definitions_reversed_decorator_order(self):
        @arg("a", type=int)
        @task
        def fun3(a,b:int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            return a + b

        ret = cli(argv=["foo", "fun3", "1", "2"], force=True)
        self.assertEqual(ret, 3)

    def test_simple3_mixed_definitions_reversed_decorator_order(self):
        @arg("a", type=int)
        @task
        @arg("b", type=int)
        def fun3(a,b):
            return a + b

        ret = cli(argv=["foo", "fun3", "1", "2"], force=True)
        self.assertEqual(ret, 3)

    def test_other_decorator_types(self):
        @mock_decorator()
        @arg("a", type=int)
        @mock_decorator()
        @task
        @mock_decorator()
        @arg("b", type=int)
        @mock_decorator()
        def fun3(a,b):
            return a + b

        ret = cli(argv=["foo", "fun3", "1", "2"], force=True)
        self.assertEqual(ret, 3)

class TestTaskCliCallsLists(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()
        print("------------")

    def test_simple_list_with_arg(self):
        @task
        @arg("a", type=int, nargs="+")
        def fun(a):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        ret = cli(argv=["foo", "fun", "1", "2", "3"], force=True)
        self.assertListEqual(ret, [1,2,3])

    def test_simple_list_with_arg2(self):
        @task
        @arg("a", type=int, nargs=3)
        def fun(a):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        ret = cli(argv=["foo", "fun", "1", "2", "3"], force=True)
        self.assertListEqual(ret, [1,2,3])

    def test_simple_list_with_arg2_raises_on_nargs_mismatch(self):
        @task
        @arg("a", type=int, nargs=3)
        def fun(a):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        argv = ["foo", "fun", "1"]
        parser = taskcli.taskcli.build_parser(argv, exit_on_error=False)
        from taskcli.taskcli import ParsingError
        with self.assertRaisesRegex(ParsingError, "the following arguments are required: a"):
            taskcli.taskcli.parse(parser, argv)


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


    def test_simple_list_without_arg_results_in_nargs_star(self):
        @task
        def fun(a:list[int]):
            assert isinstance(a, list)
            assert len(a) == 0
            return a

        argv = ["foo", "fun"]
        parser = taskcli.taskcli.build_parser(argv)
        config = taskcli.taskcli.parse(parser, argv)
        ret = taskcli.taskcli.dispatch(config, 'fun')

        self.assertListEqual(ret, [], "Should have gotten an empty list, list[int] in params should result in nargs=* ")


class TestTaskMisuse(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()
        print("------------")

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


class TestCallingOtherTasks(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()
        print("------------")

    def test_calling_other_tasks(self):
        @task
        def fun(a):
            return a

        @task
        def fun2(a):
            return fun(a)

        ret = cli(argv=["foo", "fun2", "1"], force=True)
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