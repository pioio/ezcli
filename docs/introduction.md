# `taskcli` - Introduction

`taskcli` (aka `t`) is a tool for automating tasks.
It turns a pile of simple Python functions into a snappy, powerful, and reusable CLI interfaces.

## High-level Overview
See [README.md](../README.md) in project's root.

## Basic usage

### Installation
Install it with `pip install taskcli`.

### Invokation - two ways of running it
- `t` and `taskcli` command are equivalent - by default they show all tasks which are not marked hidden (more on that later).
- `tt` is equivalent to running `taskcli --show-hidden`. Like above, but also shows any hidden tasks and groups of tasks. You can customize this command on per-project to show even more info than only the hidden tasks (e.g. show default values of optional arguments).

### Create your first `tasks.py` file.
- Run `t --init` to create a starter `tasks.py` file in the current directory.
- edit it to your liking, more on that later
- then run `t` to list the tasks defined in it.

### List tasks
By default, invoking taskcli (`t`, `tt` or `taskcli`) without any arguments causes the tool to look for the `tasks.py` in the current directory. If the file is missing, it will look for it in the parent directory, then in parent's parent, and so on.

Listing more details:
- `t` is equivalent to `t --list|-l` -- only shows mandatory and important parameters.
- `t -ll` lists tasks in more detail  -- includes all parameter, even optional ones.
- `t -lll` list tasks in even more detauls -- include all parameters, shows default values of optional parameters.
- `t -L` show all info - can be very verbose, anything in the task list that can be shown, will be shown.

### To enable tab completion
Install `argcomplete` package. It's an optional dependency of `taskcli`, it's not installed by default.

Add this to your `.bashrc` (or run in the current shell)
```
eval "$(register-python-argcomplete t)"
eval "$(register-python-argcomplete tt)"
eval "$(register-python-argcomplete taskcli)"
```


### Merging multiple `tasks.py` files
- After finding `tasks.py` , the tool imports it.
- If that file contains `tt.config.include_extra_tasks = True`, The tool will continue traversing up the directory tree, and if it encounters another `tasks.py` files it merge the tasks from it, with the current one.
- You can use `tt.config.merge_parent_filter = my_filter_function` to customize which tasks are merged in.
```python
from taskcli import tt

def my_filter_function(task):
    return task.name.startswith("deploy") or "prod" in task.tags

tt.config.merge_parent_filter = my_filter_function
```


This allows you to have a single `tasks.py` file in the root of your project, and then have additional `tasks.py` files in subdirectories, and have them all be merged together any way you like as you traverse the directory tree.




## Creating tasks

### Minimal example:
```python
from taskcli import task, tt, run
@task
def hello():
    print("Hello, World!")
    run("ls / | grep etc")

```

## the `tt` python module
The recomended way of using the library is
```python
from taskcli import task, tt, run
```
The `run` function is a simple wrapper around `subprocess.run` which prints the command before running it.
But feel free to use your own way of running command

The `tt` module is the public api of the library. It contains all the common objects and and functions a typical `tasks` file might need.

```python

tt.config.(...)  # contains the default configuration

```

## Configuration load order
- First, there's hardcoded defaults (`src/taskcli/taskcliconfig.py`)
- (future work) Config files.
- values changed in `tasks.py` via `tt.config.xxx = 'abc'` during the `task.py` module import by the Python interpreter
- values obtained with environment variables
- values obtained from the command line

In other words, command line arguments take precedence over everything else.

By design, not all fields of `tt.config` can be set via environment variables or command line. But most can be set by both.


## The `tasks.py` file - best practices
The `tasks.py` file is just a regular python script.
It can contain any python code, variable, classes, regular (non-task) functions, or import any other module.
But it's main purpose is to define tasks.

Good practice is to keep `tasks.py` contain primarly the entrypoints task definitions, and move any other code to other files.

Rule of thumb: if a task has more than 10 lines, it probably deserves to be a separate function in a separate module.

For a real-life example of a large `tasks.py`, see the [tasks.py of this project](../tasks.py), or the [tasks.py used for generating the docs](../docsgenerator/tasks.py).

You can also choose to execute a taskfile directly via `./tasks.py`. For this to work you need to include the following
at the end of the file:
```python
if __name__ == "__main__":
    tt.dispatch()
```

## Types of Tasks
All tasks are defined with `@task` decorator
A task can be important, hidden, both, or neither,
e.g.
`@task(hidden=True)`
`@task(important=True)`


Hidden tasks are not shown by default by `t`. Use `tt` to show also them.
Hidden tasks that are meant to be run relatiely inferequently.

Hidden tasks can be listed either by
- with `--show-hidden|-H` flag, or with `--list-all|-L` flag
- or by listing all tasks in specific group.

Important tasks are just that, important.
The reason depends on the cotext.
Important tasks have a special formatting (customizable), and are by default floated to the top of their group.

### Tasks and groups
Each task is always in one specific group.

## Typical usage
- run `t` to list all the (not hidden) tasks in local `./tasks.py` file. Some info is hidden from this overview.
- run `t <task_name>` to run a task.
- run `t <group_name>` to list only tasks in that group. This view includes more detailed info than the full listing.

The goal of `t` is to get a quick overview of all the tasks.
You can always include `t -L` to view all the info for all the groups. But note that for large projects
this can result in a lot of output




## Other features
- Expose regular python function into a task, print their output to stdout  (`-P` flag.)

- Integration with go-task (http://taskfile.dev).  If `TASKCLI_GOTASK_TASK_BINARY_FILEPATH` is set, any local Taskfile.yaml files are loaded automatically.

- Support for exotic parameters types. Parameters with types which cannot be converted from argparse will be gracefully ignores (so long as they have a deafult value). Future work: support for custom conversion functions.


## Automatic Directory switching

By default running a task will switch to the directory where the task is defined.
This happen both when you run the task via `taskcli`, and when you call the python function decorated with `@task` yourself.
The section below outlines how that works.
Note, `@task(change_dir=False)` will disable this behavior, and preserve whatever CWD was set right before the task function was called.

See `TASKCLI_EXTRA_TASKS_PY_FILENAMES` to customize where `taskcli` looks for `tasks.py` files in directories above the current one.


### Simple project
```markdown
project/
- tasks.py                # let's say this one haas 3 tasks
    * upload-files
    * deploy-to-prod
    * deploy-to-staging
```

Those 3 actions are available anywhere within the `project/` dir tree.
This mean you can run
`project/foo1/foo2/foo2/$ t deploy-to-prod`
without needing to switch to the root of the project first.

### Advanced project
```markdown
project/
- tasks.py     # let's say this one has the same 3 task, and one new included one.
    * upload-files
    * deploy-to-prod        # tagged as "important" within this file
    * deploy-to-staging
    * bake-cake             # included by name from  project/foo/bakery/tasks.py


project/foo/bakery/
- tasks.py                 # chooses to auto-include all 'important' tasks from project/tasks.py
    * bake-cake            # defined here, running it from anywhere switches to project/foo/bakery/
    ⬆ deploy-to-prod      # auto-included from project/tasks.py, running it switches to project/ dir
```

For example, running
project/some/other/directory $ t bake-cake
will find the task in project/tasks.py , notice it was imported from project/foo/bar/tasks.py,
will switch to project/foo/bar/ dir, and run the task in there
```