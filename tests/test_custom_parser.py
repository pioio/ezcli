import argparse
import sys

import taskcli
from taskcli import Task, task

from .utils import include_tasks, reset_context_before_each_test

sideeffect = 0


def customize_parser(parser):
    """Customize the argparse parser."""
    global sideeffect
    sideeffect += 1
    parser.add_argument("--custom-arg", default=42)


def test_parser_customization():
    """Test customizing the parser."""

    @task(customize_parser=customize_parser)
    def run():
        """Run the taskcli."""

        parsed_args = taskcli.get_runtime().parsed_args
        assert parsed_args is not None
        assert hasattr(parsed_args, "custom_arg")
        assert parsed_args.custom_arg == "999"
        assert sideeffect == 1

    tasks = include_tasks()

    assert len(tasks) == 1

    taskcli.dispatch(["run", "--custom-arg", "999"])
