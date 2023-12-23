import inspect
import unittest
from unittest import TestCase

import taskcli
from taskcli import arg, cli, task
from taskcli.taskcli import mock_decorator


class TaskCLITestCase(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()


class TestLongerCLI(TaskCLITestCase):
    def test_many_params(self):
        @task
        def fun(a, b, a_int: int, a_str: str):
            assert isinstance(a, str)
            assert isinstance(b, str)
            assert isinstance(a_int, int)
            assert isinstance(a_str, str)

        # argv = ["./foo", "fun", "aaa", "bbb", "123", "foobar"]
        argv = "./foo fun -a aaa -b bbb --a-int 123 --a-str foobar".split()
        cli(argv=argv, force=True)

    def test_many_mixed_args_and_params(self):
        @task
        @arg("a", type=float)
        @arg("b", type=str, nargs=2)
        def fun(a, b, a_int: int, a_str: str):
            assert isinstance(a, float)
            assert isinstance(b, list)
            assert isinstance(a_int, int)
            assert isinstance(a_str, str)

        argv = "./foo fun 1.1 bbb1 bbb2 --a-int 123 --a-str foobar".split()
        cli(argv=argv, force=True)

    @unittest.skip("broken, pos-a not remane to pos-a when dispatcihng")
    def test_proper_name_conversion_from_arg_to_param(self):
        @task
        @arg("pos-a", type=int)
        @arg("--param-b", type=int)
        def fun(pos_a, param_b):
            assert isinstance(pos_a, int)
            assert isinstance(param_b, int)
            pass

        argv = "./foo fun 12 --param-b 33".split()
        cli(argv=argv, force=True)

    # def test_many_mixed_args_and_params_and_options(self):
    #     @task
    #     @arg("pos-a", type=int)
    #     @arg("--option-a", type=int, nargs=2)
    #     def fun(option_a,pos_a, option_p:str="foobar"):
    #         assert isinstance(option_a, list)
    #         assert isinstance(option_a[0], int)
    #         assert isinstance(option_p, str)
    #         assert isinstance(pos_a, int)

    #     argv = "./foo fun --option-p xxx --option-a 1 42 3".split()
    #     cli(argv=argv, force=True)


class TestStuff(TaskCLITestCase):
    def test_basic(self):
        @task
        @arg("--option-a", type=int, nargs=2)
        def fun(option_a, pos_a):
            assert isinstance(option_a, list)
            assert isinstance(option_a[0], int)
            assert isinstance(pos_a, str)

        argv = "./foo fun  --option-a 1 42 --pos-a xxx".split()
        cli(argv=argv, force=True)


# specfying multiple options
