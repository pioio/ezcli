import subprocess

import taskcli
from taskcli import init

from .test_including import clean_stdout


def test_init_new_file():
    """Test that the file written with --init has a working format."""
    examples = taskcli.examples.get_examples()

    import os

    dir = "/tmp/taskcli-unit-tests"
    if not os.path.exists(dir):
        os.mkdir(dir)

    filepath = os.path.join(dir, "taskcli-example-unit-test-init.py")
    if os.path.exists(filepath):
        os.remove(filepath)

    init.create_tasks_file(filepath)
    taskcli.run(f"chmod +x {filepath}")
    taskcli.run(f"python {filepath}")

    res = subprocess.run(["python", filepath], capture_output=True)
    stdout = res.stdout.decode("utf-8")
    print(stdout)
    stdout = clean_stdout(stdout)
    assert "hello-world" in stdout, stdout
