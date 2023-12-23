from taskcli import task, run_task

def test_foobar():
    def x(z:int|None|list[str]):
        pass

    with (
         open("/tmp/foobar", "w") as foobar,
        open("/tmp/foobar", "r") as foobar2,
    ):
        pass



def test_tab_completion():
    import os
    import subprocess
    try:
        os.environ["_ARGCOMPLETE"] = "0"
        os.environ['COMP_LINE'] = 'tests/fixtures/testtabcomplete/tasks.py '  # The user's current input
        os.environ['COMP_POINT'] = str(len(os.environ['COMP_LINE']))  # Cursor position

        # Invoke your script with argcomplete
        # Replace 'yourscript' with the path to your script

        process = subprocess.Popen(
            ['tests/fixtures/testtabcomplete/tasks.py'],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,

        )

        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        # Check for specific completions in the output
        #completions = stdout.decode().splitlines()

        # Right now this only tests if code reaches specific point, but not if the completion is actually emitted
        # not sure how to check for that.
        assert stdout.decode() == "Starting completion\n"
    finally:
        del os.environ["_ARGCOMPLETE"]
        del os.environ['COMP_LINE']
        del os.environ['COMP_POINT']





def test_basic():
    x = 0
    @task
    def foobar() -> int:
        nonlocal x
        x += 1
        return 42

    assert foobar() == 42
    assert x == 1

    run_task(argv=["foobar"])
    assert x == 2


import subprocess
import os

def run_tasks(path) -> tuple[str, str]:
    process = subprocess.Popen(
            [path],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode()

def test_basic2():

    stdout, stderr = run_tasks("tests/fixtures/groups.py")
    assert stderr == ""

    lines = stdout.splitlines()
    lines = [line.strip() for line in lines]
    assert lines == [
        "*** default",
        "* task3",
        "*** foobar",
        "* task2",
        "* task1",
    ]