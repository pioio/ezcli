
from re import T
from unittest import TestCase
import unittest

import example2 as example

import logging
logging.disable(logging.CRITICAL)

class TestExample2_Lists(TestCase):
    def setUp(self):
        pass

    # all list conversion is not working now, this needs work

#@unittest.skip("FIXME")
    def test_list_ints_with_arg_but_no_type(self):

        before = ['1','2']
        after = example.list_ints_with_arg_but_no_type(before)
        self.assertListEqual(before, after)

        before = ['1',2]
        after = example.list_ints_with_arg([1,2])
        self.assertListEqual(before,after)

        before = []
        after = example.list_ints_with_arg([])
        self.assertListEqual(before,after)


    @unittest.skip("FIXME")
    def test_list_with_args(self):

        before = ['1','2']
        after = example.list_ints_with_arg([1,2])
        self.assertListEqual(before, after)

        before = ['1',2]
        after = example.list_ints_with_arg([1,2])
        self.assertListEqual(before,after)

        before = []
        after = example.list_ints_with_arg([])
        self.assertListEqual(before,after)

    @unittest.skip("FIXME")
    def test_list_ints_without_args_decorator(self):

        before = ['1','2']
        after = example.list_ints_with_arg(['1','2']) # this is now broken, it should return ints!
        self.assertListEqual(before,after)

        before = ['1',2]
        after = example.list_ints_with_arg(['1',2])  # this is now broken, it should return ints!
        self.assertListEqual(before,after)
