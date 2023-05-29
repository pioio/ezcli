from unittest import TestCase
import unittest

import taskcli
import inspect

from taskcli import cli, task, arg
from taskcli.taskcli import mock_decorator


class TaskCLITestCase(TestCase):
    def setUp(self) -> None:
        taskcli.taskcli.cleanup_for_tests()


# TODO:
# prevent foo(a:list[list[int]]) and other weird complex types if a matching 'arg' is not specified
