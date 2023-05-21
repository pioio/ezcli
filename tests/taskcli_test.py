from unittest import TestCase

import taskcli
import inspect

from taskcli import cli, task, arg

class TestTaskcli(TestCase):

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
        def fun(a,b):
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