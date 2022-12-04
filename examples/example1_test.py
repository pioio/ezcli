

import unittest
from unittest import TestCase
from click.testing import CliRunner

import example

class TestExample(TestCase):

    def setUp(self):
        self.maxDiff = 3000

    def test_example(self):
        runner = CliRunner()
        result = runner.invoke(example.cli)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Usage:\n" in result.output)
        self.assertTrue("file, f, fi" in result.output)

    def test_file_cli(self):

        runner = CliRunner()

        # via full name
        result = runner.invoke(example.cli, "file")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage:\n", result.output)
        self.assertNotIn("file, f, fi", result.output)
        self.assertIn("create, c", result.output)

        # via alias
        result = runner.invoke(example.cli, "f")
        self.assertTrue("Usage:\n" in result.output)
        self.assertTrue("file, f, fi" not in result.output)
        self.assertTrue("create, c" in result.output)

    def test_providing_mandatory_argument(self):
        runner = CliRunner()

        result = runner.invoke(example.cli, "file create foobar")
        self.assertIn("Creating a file foobar", result.output)
        self.assertEqual(result.exit_code, 0)

        # via group alias
        result = runner.invoke(example.cli, "f create foobar")
        self.assertIn("Creating a file foobar", result.output)
        self.assertEqual(result.exit_code, 0)


        # via command alias, argument required, and provided
        result = runner.invoke(example.cli, "file c foobar")
        self.assertIn("Creating a file foobar", result.output)
        self.assertEqual(result.exit_code, 0)

        # via group and command alias, argument required, and provided
        result = runner.invoke(example.cli, "f c foobar")
        self.assertIn("Creating a file foobar", result.output)
        self.assertEqual(result.exit_code, 0)


class TestGreet(TestCase):

    def setUp(self):
        self.maxDiff = 3000

    def test_not_providing_optional_argument(self):
        runner = CliRunner()

        result = runner.invoke(example.cli, "greet user")
        self.assertIn("Hello, unknown user!", result.output)
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(example.cli, "g u")
        self.assertIn("Hello, unknown user!", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_providing_optional_argument(self):
        runner = CliRunner()

        result = runner.invoke(example.cli, "greet user foobar")
        self.assertIn("Hello, foobar!", result.output)
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(example.cli, "g u")
        self.assertIn("Hello, unknown user!", result.output)
        self.assertEqual(result.exit_code, 0)


    def test_providing_optional_option(self):
        runner = CliRunner()

        result = runner.invoke(example.cli, "greet say-hello --message=Hi")
        self.assertEqual("Hi!\n", result.output)
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(example.cli, "g sh --message=Hi")
        self.assertEqual("Hi!\n", result.output)
        self.assertEqual(result.exit_code, 0)


    def test_not_providing_optional_option(self):
        runner = CliRunner()

        result = runner.invoke(example.cli, "greet say-hello")
        self.assertEqual("Hello!\n", result.output)
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(example.cli, "g sh")
        self.assertEqual("Hello!\n", result.output)
        self.assertEqual(result.exit_code, 0)
