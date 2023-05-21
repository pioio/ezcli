from unittest import TestCase

import taskcli
import inspect

from taskcli import cli, task, arg

class TestTaskcli(TestCase):

    def test_fun_rerunning_cli_works(self):
        @task
        @arg("a", type=int, nargs="+")
        def fun(a:list[int]):
            assert isinstance(a, list)
            assert isinstance(a[0], int)
            return a

        argv = ["foo", "fun", "1", "2", "3"]
        ret = cli(argv=argv, force=True)
        ret = cli(argv=argv, force=True)

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
