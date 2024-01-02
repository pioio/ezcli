"""Most basic example of a task.

Tags: basic

Run:
- t -f FILENAME                 # list tasks
- taskcli -f FILENAME           # list tasks, equivalent to 't'
- tt -f FILENAME                # list tasks, including hidden ones
- t -f FILENAME hello           # run the hello taask
- t -f FILENAME hello-hidden    # run the hidden task

"""
from taskcli import task, tt


@task
def hello():
    """This line will become the summary for the task list output."""
    print("Hello, World!")


@task(hidden=True)
def hello_hidden():
    """This task is hidden by default.

    You can run it with `t`, even though it's not shown in the task list by default.
    """
    print("Hello from the hidden task!")
