import inspect
import unittest
from unittest import TestCase

import taskcli
from taskcli import arg, cli, task
from taskcli.taskcli import mock_decorator


class TaskCLITestCase(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()


# TODO:
# prevent foo(a:list[list[int]]) and other weird complex types if a matching 'arg' is not specified
