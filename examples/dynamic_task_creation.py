"""Create tasks dynamically.

And to make it interesting, each task has a different default argument.

Tags: basic

Run:
- taskcli -f FILENAME               # list tasks
- taskcli -f FILENAME  foobar-1
- taskcli -f FILENAME  foobar-5 --person-name Lex
- taskcli -f FILENAME  call-all-dynamic-foobars

"""

from taskcli import task, tt

# Different default args for each task
names = ["Alice", "Bob", "Charlie", "Dylan", "Eve", "Frank", "Grace", "Helen"]

for x in range(7):
    # To avoid name clashes, we will need to assign unique name to each task.
    task_name = f"foobar-{x}"

    person_name = names[x]

    @task(name=task_name, desc=f"Task number {x}")
    def foobar(x=x, *, person_name=person_name):  # x=x is needed to bind the loop variable (important!)
        print(f"Hello, {person_name}! ".ljust(20) + f"({x=})")


@task
def call_all_dynamic_foobars():
    """Call all the dynamically created tasks."""
    tasks = tt.get_tasks()  # returns all the tasks present in this module
    for task in tasks:
        if task.name.startswith("foobar"):
            task.func()