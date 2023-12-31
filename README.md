# `taskcli` - simple, powerful, reusable, and browsable CLI interfaces from Python functions.

`taskcli` is a library and tool for creating and managing CLI interfaces for your projects and automation.

At its core, `taskcli` is two things:
- The `taskcli` Python library for exposing Python function as powerful CLI interfaces (each function becomes a "Task" you can run)
- The `t` CLI tool for browsing, grouping, and running your Tasks (using tags, namespaces, hierarchical groups, custom filter functions, regex search, imports, aliases!)

`taskcli` can be use for any project, any task, language.
It's a replacement for chaotic collections of shell scripts, YAML files, and Makefiles.

All this allows you to focus on your project, or on automating your Tasks and workflows.

Your Task entrypoints are defined in Python (which makes them infinitely flexible), but they can do whatever you want:
- Build a Rust or Node Web app,
- Ship a file, build a container
- Run an ansible playbook, restart a server,
- make coffee, send a message, prepare a report
- etc.

Taskcli keeps your tasks (cli entrypoints) organized, clean, discoverable, reusable, modular, self-documenting, and easy to use.

See further below for comparions to other similar tools.

## Documentation Overview
- Overview -- This document
- [Introduction](docs/introduction.md) - How to use `taskcli` for your projects.
- [Usecases](docs/usecases.md) - Different ways in which you can use `taskcli` for your projects.
- [Examples](docs/examples.md) - Complete executable examples from the `examples/` dir, along with sample output.
- [Cheat sheet](docs/cheatsheet.md) - Code snippets -- quick reference of the most important features.
- [Settings](docs/settings.md) - List of all the settings that can be customized via env vars or CLI.
- [Troubleshooting](docs/troubleshooting.md) - Tips and trick for troubleshooting common issues.
- [TODOs](docs/todo.md) - List of ideas for future work, known issues, etc.
- [Developer documentation](docs/dev.md) - nitty gritty implementation details for contributors.


## Quickstack example
First, install it `pip install taskcli`

Then, all you need is a `tasks.py` file with one or more function decorated with `@task`:
```python
$ cat tasks.py
from taskcli import task
@task
def hello(name="Bob", *, count=1):
    for i in count:
        print(f"Hello, {name}!")
```
Now you can run it in one of several ways:
- `t hello`
- `t hello Alice`
- `t hello Alice`
- `t hello --count 10`
- `t hello -c 10 Alice`, etc.

The CLI arg syntax was auto-determined from the function signature.

(Note: the `t` and `taskcli` commands are equivalent)

## Key features of `taskcli`
- Automatic generation of CLI interfaces from signatures of simple Python functions.
- You can group, highlight, tag, hide, list, regex-search your tasks.
- Write tasks by hand, or create them programmatically, or do a mix both.
- See all your tasks at a glance -- see which tasks require additional env vars, and which require specifying mandatory arguments.
- Import and reuse(!) tasks from other modules/dirs  (`tt.include(module_name)`). Directories will be switched automatically if needed.
- Less noise -- auto hide tasks which are not ready to be run (e.g. due to missing env vars) (`tt.config.hide_not_ready = True`)
- Quickly see the overview of all the tasks, along with optional and mandatory arguments.
- Customize the way your tasks are listed. Customize it on per-project basis, or globally for many projects.
- Simple to start, but power and suitable for managing larger projects.
- Automatically switch directories when running tasks imported from other directories (can be disabled).
- Easier collaboration - customize the behavior and the look and feel of `taskcli` using env vars. Make it work for you the way ***you*** like it, while keeping the shared project codebase generic.

## Basic usage quickstart
- `pip install taskcli` - install it
- `t --init` creates a blank `tasks.py` file in the current directory with example content.
- `t` list all the tasks defined by the `tasks.py` located in current directory (or in parent directory - auto discovery).
- `t <task-name> [args]` run a task (tool will automatically switch directories if needed), `[args]` are passed directly to the task function.
- `t <group-name>` list all the tasks in a group of tasks (also the hidden ones).
- `t -s <search-term>` list all the tasks matching the regex search term.
- `t -t tags` list all the tasks with the given tags.
- `t -t imp` list all tags marked as important.
- `t -H` list all the tasks, even the ones marked as hidden and the onces in hidden group.


## Screenshot
TODO

## Another example:
```python
$ cat tasks.py
from taskcli import task, run

@task(aliases="b")
def bake(frosting: str = "chocolate", *, eat: bool = True):
    run(f"bake-my-care --cake {frosting} && eat")
    if eat:
        print("Yummy!")
```
And run it, e.g.: `t bake` or `t bake --frosting cream` or `t b` or `t b -f vanilla --no-eat`, etc.

That's it! All the flags are generated automatically, including the `--no-*` bool variants.


The overall CLI format is:
`t <taskcli-options> task-name <task-specific-options>`


## What is it for?
`taskcli` is designed for automating tasks. Any tasks.

It can work with any type of project -- it's definately not only for Python.
The `taskcli` tasks simply happen to be defined in Python, instead of in YAML.
This makes `taskcli` tasks **easier to work it, refactor, test, and maintain.**

If you ever tried to maintain and refactor large YAML codebases file, you know **exactly** what I mean.

The tasks, once defined, can do whatever you want.
Often, they will be a mix Python, and running shell commands and external tools using e.g. provided `run` functions.
It's up to you whether you want to lean more towards Python, or more towards shell commands.

The guiding design principles of `taskcli` are:
- make running and navigating between tasks easy & fast.
- show only what's needed, but make it easy to drill down and reveal more info.
- make the most important tasks stand out. Hide the less frequently used ones, but make them easy to find and use.


## The entrypoints - `t` vs `tt` - see less vs more
By default `taskcli` installs these three entrypoints: `t`, `tt`, `taskcli`
- `t` and `taskcli` are equivalent; they are the canonical entrypoints to the tool.
- `tt` is an alternative entrypoint. It's designed to show a bit more info by default.
  By default it's the equivalent of running `t --show-hidden`.
  Meaning that `tt` shows all the hidden tasks and groups.

Why two ways of running the command?
Switching between `t` and `tt` is be the fastest way of toggling between showing less vs more info

You can customize both `t` and `tt` entrypoints on per-project basis by adding more default flags.
For example, you can make `tt` also show values of default arguments:
```
from taskcli import tt
tt.config.default_options_tt = ["--show-optional-args"]
```
(the 'taskcli.tt' python module contains the public API of the library, it just happens to be called like `tt` cli tool).


## Disclaimer
This library is still in early development. API will continue to rapidly evolve. Be sure to pin the version.
If you need a more mature, less rapidly changing solution, consider using [pyinvoke](https://www.pyinvoke.org/) or Taskfile.dev.

## Roadmap and major TODOs
- post/pre task hooks that run only once
- chaining tasks  `taskcli task1 --task-arg1 task2 --arg-for-task2`
- including files via HTTP
- config file support

## Prior art and comparison
### pyinvoke
`taskcli` is very similar to `pyinvoke`, and builds on many of its ideas.

Differences
- `taskcli` automatically assumes real-life tasks often come with co-located files, so by default it automatically switches directories
    when running tasks imported from other directories. This can be disabled.
- Unlike pyinvoke, `taskcli` does away with explitic context object that needs to be passed around. This makes defining tasks easier.
- `taskcli` aims to provides a richer task list output and overview out of the box.
- `taskcli` infers more information from type annotations, this means less duplicating information in decorators.
- `taskcli` offers more elaborate include capability, and hierarchical discovery of tasks.
- `taskcli` user experience is more opinionated, aiming to out of the box reduce the amount of keystrokes needed to navigate and tasks.
- `pyinvoke` is older, much more mature, and more battle tested.

### Taskfile.dev
Unlike Taskfile, `taskcli` does not rely on YAML.
YAML has its benefits, but also drawbacks. Refactoring large YAML collections it's not easy.
That said, a key benefit of the https://Taskfile.dev project is that it ships as a single portable `task` GO binary.

### argh
`argh` is a great, lesser knonw, library for creating CLI interfaces from python functions.
It can also be used for creating simple tasks.
Similarly to `taskcli` it also builds on top of `argparse` using type annotations and function signatures.
Unlike `argh`, `taskcli` is designed for creating and interfacing with more complex collections of reusable tasks.

## Acknowledgements
- The idea for `taskcli` was inspired by Taskfile.dev and `Justfile` projects.
- This library builds on many ideas from the excellent `argh` project. If you like the idea of building CLI interfaces from python function signatures, and don't need the advanced task management features of `taskcli`, you should check `argh` out.
- `taskcli` library uses `argparse` and `argcomplete` (argcomplete is an optional dependency for tab completion).
- markdown screenshots generated using  `ansitoimg` and `termtosvg`.