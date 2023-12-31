# Cheat sheet


This document contains short, condensed, snippets of using `taskcli`.

If you're looking for larger, executable, standalone examples, see the [examples](examples.md) document.

([click here to go the main index](../README.md))
## Basic usage
```python
# The recommended way to import taskcli is the following.
# It's implicitly used by all subsequent snippets in this page.
from taskcli import task, tt, run

# --------------------------------------------------------------------------
# Create a simple task in `./tasks.py`, run it with `t foobar`
@task
def foobar():
    print("Hello, World!")

# --------------------------------------------------------------------------
# Run a shell command, prints output to the current console
@task
def foobar():
    run("ls -la /etc/* | grep passwd")
    # Feel free to use other means of running commands, e.g. popen, or os.system


# --------------------------------------------------------------------------
# Create a simple task, with two aliases
@task
def foobar(aliases=["f", "foo"]): # also accepts a string:  aliases='f'
    ...


# --------------------------------------------------------------------------
# Mark task as important, with aliases
# Important tasks float to the top of the list, and can have special formatting
@task(important=True)
def foobar():
    ...

# --------------------------------------------------------------------------
# Hide the task from default listing of `t` command, it will be shown when using `tt`
@task(hidden=True)
def foobar():
    ...
```

## Groups and group namespaces
```python
# --------------------------------------------------------------------------
# Create a group and a task in that group, using a context manager
with tt.group("My Group"):
    @task
    def foobar():
        ...

# --------------------------------------------------------------------------
# Create a group and a task in that group, using a variable
group = tt.group("My Group")
@task(group=group)
def foobar():
    ...

# --------------------------------------------------------------------------
# Create a group that also prefixes all tasks with a namespace
with tt.group("My Group", name_namespace="mygroup"):
    @task
    def foobar():
        ...

# --------------------------------------------------------------------------
# Create a group that also prefixes all task names with a namespace
# as well as any aliases with a separate (often shorter) namespace
with tt.group("My Group", name_namespace="mygroup", alias_namespace="g"):
    @task(aliases="f")
    def foobar():
        ...
    # the resulting alias name will be "gf"
    # the resulting task name  will be 'mygroup.foobar'


# --------------------------------------------------------------------------
# Create nested group hierarchy, task list will be appropriately indented
with tt.group("My Group"):
    @task
    def foobar():
        ...
    with tt.group("My Second Group"):
        @task
        def bar():
            ...
    with tt.group("My Third Group"):
        @task
        def baz():
            ...
```

## Importing, including, and reusing other `tasks.py` files
```python
# --------------------------------------------------------------------------
# Include all tasks from another file to the default group of the current tasks.py
from package import module
tt.include(module)

# --------------------------------------------------------------------------
# Include specific, dynamically selected, tasks from another file
from package import module
def filter_fun(task):
    return task.important or task.name.startswith("deploy")
    # or, e.g.:   return 'prod' in task.tags

tt.include(module, filter=filter_fun)

# --------------------------------------------------------------------------
# import a specific selected task from another file
from package.module import mytask
tt.include(mytask)

# --------------------------------------------------------------------------
# import tasks into to a group
from package import module
with tt.group("My Group"):
    tt.include(module)

# --------------------------------------------------------------------------
# import tasks to a namespace,
from package import module
tt.include(module, name_namespace="namespace", alias_namespace="ns")

# --------------------------------------------------------------------------
# import tasks to a namespace, don't prefix existing aliases with anything
from package import module
tt.include(module, name_namespace="namespace")

# --------------------------------------------------------------------------
# import tasks into a group and into separate namespaces
from package import module1, module2
with tt.group("My Group"):
    tt.include(module1, name_namespace="one", alias_namespace="ns1")
    tt.include(module1, name_namespace="two", alias_namespace="ns2")
```

## Advanced Examples
```python
# --------------------------------------------------------------------------
# programatically modify selected all tasks

@task
def task1_do_this():
    ...

(...)

@task(tags=["prod"])
def task30_do_something_else():
    ...

for task in tt.get_tasks():
    if 'prod' in task.tags:
        task.important = True
    else:
        task.tags.add("dev")


# --------------------------------------------------------------------------
# Programatically create 10 tasks
# See an example on this in the 'examples/' dir for a
# much more detailed implementaion
for x in range(10):
    @task(name=f"foobar-{x}")
    def foobar(x=x): # x=x is needed to bind the loop variable (important!)
        print(f"Hello, World! {x=}")


```

