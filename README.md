# `taskcli` - a novel way of creating complex, real-life CLI interfaces from python functions

A tool for turning Python functions into powerful CLI interfaces for **fast** real-life task automation.

It's kind of like a Makefile, but in Python, and on steroids (search, tags, grouping, highlighting, etc).

The guiding design principles of taskcli are:
- encapsulate complexity of managing many tasks: show only what's needed, but make it easy to reveal more.
- make running and navigating between groups of tasks fast, but powerful.
- make the most important tasks stand out. Hide the less frequently used ones.

`taskcli` is not only for Python project.

It can be used for any sort of project, with Python as the glue.

## Basic usage overview
`t` list all the tasks defined by the `tasks.py` in current directory (you can import tasks from other directories)
`t <task_name> [args]` run a task (tool will automaticlly switch directories if needed)
`t <group_name>` list all the tasks in a group of tasks (also the hidden ones)
`t -s <search_term>` list all the tasks matching the regex search term
`t -t tags` list all the tasks with the given tags
`t -t imp` list all tags maked as important
`t -H` list all the tasks, even the onces marked as hidden and the onces in hidden group

(You can also use `taskcli` instead of `t`)


## The entrypoints - `t` vs `tt` - less vs more
By default `taskcli` installs these entrypoints: `t`, `tt`, `taskcli`
- `t` and `taskcli` are equivalent; they are the default entrypoints to the tool.
- `tt` is an alternative entrypoint designed to show a bit more info by default. By default it's the equivalent of running `t --show-hidden` (i.e. `t -H`), so, by default it shows all the hidden tasks and groups.

This distinction also impacts tab completion. Tab completion for `t` only shows not hidden groups/tasks, while tab completion for `tt` shows all groups/tasks.
You can customize either entrypoint by adding more default flags (e.g. to make `tt` also show values of default arguments) by customizing `tt.config` object in your `tasks.py`.

Rationale for many entrypoints: in practice I found simply switching between `t` and `tt` to be the fastest way of toggling between showing some, vs. all, tasks. Wasteful? A bit, maybe. Handy? You bet!


## Key features
- Pythonic way of defining tasks - simply create a function.
- Easily manage, group, highlight, tag, list your tasks.
- Auto hide tasks which are not ready to be run (e.g. due to missing env vars) (`tt.config.hide_not_ready = True`)
- Import and reuse tasks from other modules/dirs  (`tt.include(module_name)`). Directories will be switch autmtically as needed.
- Quickly see the overview of all the tasks, along with optional and mandatory arguments.
- Customize the way your tasks are listed. Customize it on per-project basis, or globally for many projects.
- Configurable: easy to start, but also easy to customize for larger projects.
- Automatically switch directories when running tasks imported from other directories (can be disabled).



## Tab completion
Install `argcomplete` package. It's an optional dependency of taskcli

Add this to your `.bashrc`
```
eval "$(register-python-argcomplete taskcli)"
eval "$(register-python-argcomplete tt)"
```

## Installation and basic usage
```
# Install the package
pip install taskcli

# Create a ./tasks.py file in the current directory with example content
taskcli --init

# list the tasks in tasks.py
taskcli <task_name>

# Instead of `taskcli` you can also use the `t` script, eg:
t
t <task_name>
```

## Overview
All projects revolve around performing small tasks.
Be it complication, deployment, testing, making an API call, or anything else, it's all just a task.
As projects grow, so does the number of tasks.
Over time, it becomes harder and harder to organize them.

This tool aims to solve this problem by providing means of not only easily creating tasks,
but also easily navigating them later on.
You can group tasks, highlight the important ones, combine tasks from many files and directories.



### Tasks
A task can be important, hidden, both, or neither

Important tasks

Hidden tasks are not listed by default. Those are tasks that are meant to be ran relatiely inferequently.
Hidden tasks can be listed either by
- with `--show-hidden|-H` flag, or with `--list-all|-L` flag
- or by listing all tasks in specific group.

Important tasks are just that, important.
The reason depends on the cotext.
Important tasks have a special formatting (customizable)

### Tasks and groups
Each task is always in one specific group.
By defaylt, thats the default group.
You can create custom groups.

Each task has a namespace.
TODO: explain

## Typical usage
- run `t` to list all the (not hidden) tasks in local `./tasks.py` file. Some info is hidden from this overview.
- run `t <task_name>` to run a task.
- run `t <group_name>` to list only tasks in that group. This view includes more detailed info than the full listing.

The goal of `t` is to get a quick overview of all the tasks.
You can always include `t -L` to view all the info for all the groups. But note that for large projects
this can result in a lot of output

## Listing tasks
- `tt` is equivalent to `tt --list|-l` -- only shows mandatory and important parameters.
- `tt -ll` lists tasks in more detail  -- includes all parameter, even optional ones.
- `tt -lll` list tasks in even more detauls -- include all parameters, shows default values of optional parameters.




## Main features
- Optimized for fast startup (majority of startup time is python interpreter startup). Benchmark with `TASKCLI_ADV_PRINT_RUNTIME=1`
- Easy to start, flexible when needed (access to underlying `argparse` parser)
-

## Other features
- Expose regular python function into a task, print their output to stdout  (`-P` flag.)

- Integration with go-task (http://taskfile.dev).  If `TASKCLI_GOTASK_TASK_BINARY_FILEPATH` is set, any local Taskfile.yaml files are loaded automatically.

- Support for exotic parameters types. Parameters with types which cannot be converted from argparse will be gracefully ignores (so long as they have a deafult value). Future work: support for custom conversion functions.

## Customisation
`taskcli` comes with sane defaults out of the box, but it can be

### Customize Argparse parser
TODO: see cookbook


### Make certain tasks stand out by marking them as important
```
@task(important=True)
def do_something():
    ...
```

### Hide tasks from default listing
```
@task(hidden=True)
def do_something():
    ...
```

### Customize the way tasks are listed, e.g. add a red "prod!" suffix to some
```
prod_warning = "name {red}(production!){clear}"
@task(format=prod_warning)
def do_something():
    pass
```

### other
- customize default formatting string
- ...

## Design consideration
- `taskcli` shows if your env is ready to run a task. Many tasks need special env variables set.
   It's useful to see at a glance which tasks are ready to run, and which are not.
   Specify either env var names, or  for advanced cases, a function that returns a string.

## Roadmap
- Custom env validation functions


## Disclaimer
This library is still in early development and API will continue to change.
If you need a more mature solution, consider using [pyinvoke](https://www.pyinvoke.org/) or Taskfile.dev.

## Prior art and comparison
### pyinvoke
`taskcli` is very similar to pyinvoke, and builds on many of its ideas.

- `taskcli` automatically assumes real-life tasks often come with co-located files, so by default it automatically switches directories
    when running tasks imported from other directories. This can be disabled.
- Unlike pyinvoke, `taskcli` does way with explitic context object that needs to be passed around. This makes defining tasks a bit easier.
- `taskcli` aims to provides a richer task list output and overview out of the box.
- `taskcli` infers more information from type annotations, relying less on duplicating information in decorators.
- `taskcli` offers more elaborate include capability, and hierarchical discovery of tasks.
- `taskcli` user experience is more opinionated, aiming to out of the box reduce the amount of keystrokes needed to navigate and tasks.

Note, unlike pyinvoke, taskcli is still in development.

### Taskfile.dev
Unlike Taskfile, `taskcli` does not rely on YAML. It's pure python.
YAML has its benefits, but also drawbacks.

### argh
`argh` is a great library for creating CLI interfaces from python functions.
It can also be used for creating simple tasks.


## Acknowledgements
- The idea was inspired by Taskfile.dev and `Justfile`
- This library builds on many ideas from the excellent `argh` project. If you like the idea of building CLI interfaces from python function signatures, but don't need the advanced task-like features, check `argh` out.
- The library uses `argparse` and `argcomplete` behing the scenes.



## FAQ
Q: why no namespace by default?
A: in most cases it just requires additional unnecessary keystrokes. If you feel you need namespaces, you can add them manually.