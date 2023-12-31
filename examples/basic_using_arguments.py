"""Most basic example of a task.

Tags: basic

Run:
- taskcli -f FILENAME               # list tasks
- taskcli -f FILENAME  task1  100   # task1 requires the argument
- taskcli -f FILENAME  task1  100  bruno  # task1 requires the argument
- taskcli -f FILENAME  task2        # task2 does not require any args
- taskcli -f FILENAME  task2  --name bob
- taskcli -f FILENAME  task2  --name bob 193

"""
from taskcli import task, tt

@task
def task1(age: int, name: str = "alice"):
    """This task has two positional arguments, one of them is optional."""
    # The basic types are already converted to their correct types
    assert isinstance(age, int)
    assert isinstance(name, str)
    print(f"Hello from task1: {age=} {name=}")

@task
def task2(height: int = 42, *, name: str = "alice"):
    """This task has one positional, and one named optional argument.

    The args after the "*" are named options only (i.e. --name).
    """
    print(f"Hello from task2: {height=} {name=}")
