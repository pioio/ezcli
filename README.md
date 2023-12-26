# `taskcli` - a library for pragmatic and powerful CLI tools

A tool for turning Python functions into powerful CLI interfaces for **fast** real-life task automation.

The guiding design principle is to make running and navigating tasks fast -- with fewest keystrokes.

It's like a Makefile, but in Python.


## Overview
All projects revolve around performing small tasks.
Be it complication, deployment, testing, making an API call, or anything else, it's all just a task.
As projects grow, so does the number of tasks.
Over time, it becomes harder and harder to organize them.

This library aims to solve this problem by providing means of not only easily creating tasks,
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


## Design consideration
- `taskcli` shows if your env is ready to run a task. Many tasks need special env variables set.
   It's useful to see at a glance which tasks are ready to run, and which are not.
   Specify either env var names, or  for advanced cases, a function that returns a string.

## Readmap
Custom env validation functions


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

## Key features
- Pythonic way of defining tasks - simply create a function.
- Easily manage, group, highlight, list your tasks.
- Import and reuse tasks from other modules/dirs.
- Quickly see the overview of all the tasks, along with optional and mandatory arguments.
- Customize the way your tasks are listed. Customize it on per-project basis, or globally for many projects.
- Configurable: easy to start, but also easy to customize for larger projects.
- Automatically switch directries when running tasks imported from other directories (can be disabled).

## Acknowledgements
- The idea was inspired by Taskfile.dev and `Justfile`
- This library builds on many ideas from the excellent `argh` project. If you like the idea of building CLI interfaces from python function signatures, but don't need the advanced task-like features, check `argh` out.
- The library uses `argparse` and `argcomplete` behing the scenes.

