
from re import T
from unittest import TestCase

import example1 as example

import logging
logging.disable(logging.CRITICAL)

class TestExample1(TestCase):
    def setUp(self):
        pass

    def test_bool(self):
        data = [
            ("True", True),
            ("False", False),
            ("0", False),
            ("000", True),
        ]

        for idx, d in enumerate(data):
            self.assertEqual(example.abool(d[0]), d[1], msg=f"Failed for items {idx}")

    def test_calling_via_other_task_works(self):
        example.call_abool()

    def test_add_not_typed(self):
        self.assertEqual(example.add_no_type("a", "b"), "ab")
        self.assertEqual(example.add_no_type("1", "2"), "12")

        with self.assertRaises(AssertionError):
            example.add_no_type(1, 2)

    def test_add_typed_throws_when_given_letters(self):
        with self.assertRaises(ValueError):
            self.assertEqual(example.add("a", "b"), "ab", "Should fail to conver letter to int")

    def test_add_typed_int(self):
        self.assertEqual(example.add("1", "2"), 3, "Should have gotten converted")
        self.assertEqual(example.add(1, "2"), 3, "Should have gotten converted")
        self.assertEqual(example.add(1, 4), 5)

    def test_add_typed_float(self):
        self.assertAlmostEqual(example.add_floats("1", "2"), 3.0, "Should have gotten converted")
        self.assertAlmostEqual(example.add_floats(1, "2"), 3.0, "Should have gotten converted")
        self.assertAlmostEqual(example.add_floats(1.0, 4), 5.0)