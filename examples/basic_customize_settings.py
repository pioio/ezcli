"""Most basic example of a task.

Tags: basic

Run:
- taskcli -f FILENAME             # list tasks
- taskcli -f FILENAME  task1      # will call second task several time
- taskcli -f FILENAME  say-hello yeti # call it directly
"""
from taskcli import task, tt

# Here we change the default, to print a message whenever we enter a task
tt.config.print_task_start_message = True


@task
def task1():
    """This task has two positional arguments, one of them is optional."""
    print("Starting the first task", flush=True)
    say_hello("alice")
    say_hello("bob")
    say_hello("charlie")

    # But we can choose to disable it for this call, simply change it at any time
    # >  tt.config.print_task_start_message = False
    say_hello("dylan")


@task
def say_hello(name="alice"):
    """This task has one positional, and one named optional argument.

    Args after the "*" are named options only.
    """
    print(f"Hello from task2, {name=}", flush=True)
