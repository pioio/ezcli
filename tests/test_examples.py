"""Tests the baked in code examples."""


import pytest
import taskcli
from taskcli.examples import Example, RunCommand
import subprocess

# examples = taskcli.examples.get_examples()


def test_loading_examples():
    res = taskcli.examples.load_examples("examples/")
    assert len(res) > 0


import os


@pytest.mark.parametrize("example", taskcli.examples.load_examples("examples/"), ids=lambda e: e.title)
def test_one_example(example: Example):

    print("Testing example:", example.title)
    taskcli.examples.run_example(example, RunCommand(desc="list tasks", cmd="taskcli -f " + example.filepath))

    runcommands = taskcli.examples.get_run_commands(example, filename=example.filepath)
    for runcmd in runcommands:
        taskcli.examples.run_example(example, runcmd=runcmd)


# def test_broken_example_raises():
#     example = taskcli.examples.Example(
#         title="broken",
#         text="""
# @task
# def ok():
#    assert True

# @task
# def bad_assert():
#     assert False
# """,
#     )
#     taskcli.examples.run_example(example, argv=[])
#     taskcli.examples.run_example(example, argv=["ok"])

#     with pytest.raises(subprocess.CalledProcessError):
#         taskcli.examples.run_example(example, argv=["bad_assert"])
#     with pytest.raises(subprocess.CalledProcessError):
#         taskcli.examples.run_example(example, argv=["nonexisting-task"])

# def test_print_examples():
#     taskcli.examples.print_examples()
