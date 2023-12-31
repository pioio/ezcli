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


def test_broken_example_raises():
    filepath = "/tmp/taskcli-unittest-broken-example.py"
    example = taskcli.examples.Example(
        title="broken",
        filepath=filepath,
        file_content="""
@task
def ok():
   assert True

@task
def bad_assert():
    assert False
""",
    )
    with open(filepath, "w") as f:
        f.write(example.file_content)

    runcmd = taskcli.examples.RunCommand(desc="run ok", cmd="taskcli -f " + example.filepath + " ok")
    taskcli.examples.run_example(example, runcmd)
    taskcli.examples.run_example(example, runcmd)

    with pytest.raises(subprocess.CalledProcessError):
        runcmd = taskcli.examples.RunCommand(desc="run ok", cmd="taskcli -f " + example.filepath + " bad-assert")
    with pytest.raises(subprocess.CalledProcessError):
        runcmd = taskcli.examples.RunCommand(desc="run ok", cmd="taskcli -f " + example.filepath + " non-existing-task")

