# `taskcli` - powerful, reusable, and robust CLI interfaces from simple Python functions.

The `t` (`taskcli`) CLI tool for **fast**, real-life, task automation for fans of the Linux command shell.

Save time - create snappy, powerful, and reusable CLI interfaces from simple Python functions.

Navigate & use your task with ease, also in large projects -- tags, search, imports, aliases, namespace, groups!

Manage and automate task of any project (not only Python)!


## Quickstack
Install: `pip install taskcli`

Then, all you need is a `tasks.py` file with a single simple function:
```
$ cat tasks.py
from taskcli import task
@task
def hello(name="Bob"):
    print(f"Hello, {name}!")
```
And you can run it: `t hello` or `t hello -n Alice` or `t hello --name Alice`

## Key features
- You can group, highlight, tag, hide, list, regex-search your tasks.
- Import and reuse(!) tasks from other modules/dirs  (`tt.include(module_name)`). Directories will be switched automtically as needed.
- Less noise -- auto hide tasks which are not ready to be run (e.g. due to missing env vars) (`tt.config.hide_not_ready = True`)
- Quickly see the overview of all the tasks, along with optional and mandatory arguments.
- Customize the way your tasks are listed. Customize it on per-project basis, or globally for many projects.
- Simple to start, but power and suitable for managing larger projects.
- Automatically switch directories when running tasks imported from other directories (can be disabled).
- Easier collaboration with others - customize the behavior and the look and feel of `tasks` using env vars.


## Another example:
```
$ cat tasks.py
from taskcli import task, run

@task(aliases="b")
def bake(frosting: str = "chocolate", *, eat: bool = True):
    run(f"bake-my-care --cake {frosting} && eat")
    if eat:
        consume()
@task
def eat():
    print("Yum yum!")

```
And run it, e.g.: `t bake` or `t b` or `t b -f vanilla --no-eat`

That's it!


## Basic usage
- `t --init` creates a blank `tasks.py` file in the current directory with example content.
- `t` list all the tasks defined by the `tasks.py` located in current directory (or in parent directory - auto discovery).
- `t <task_name> [args]` run a task (tool will automatically switch directories if needed), `[args]` are passed directly to the task function.
- `t <group_name>` list all the tasks in a group of tasks (also the hidden ones).
- `t -s <search_term>` list all the tasks matching the regex search term.
- `t -t tags` list all the tasks with the given tags.
- `t -t imp` list all tags marked as important.
- `t -H` list all the tasks, even the ones marked as hidden and the onces in hidden group.


## What is it for?
`taskcli` is designed for automating tasks. Any tasks.

It can work with any type of project -- it's definately not only for Python.
The `taskcli` tasks simply happen to be defined in Python, instead of than in YAML.
This makes `taskcli` tasks **easier to work it, refactor, test, and maintain.**

If you ever tried to maintain and refactor large YAML codebases file, you know **exactly** what I mean.

The tasks, once defined, can do whatever you want.
Often, they will be a mix Python calls/flow, and running shell commands and external tools using e.g. provided `run` functions.
It's up to you whether you want to lean more towards Python, or more towards shell commands.

The guiding design principles of `taskcli` are:
- make running and navigating between tasks easy fast.
- show only what's needed, but make it easy to drill down and reveal more info.
- make the most important tasks stand out. Hide the less frequently used ones, but make them easy to find and use.


## The entrypoints - `t` vs `tt` - see less vs more
By default `taskcli` installs these three entrypoints: `t`, `tt`, `taskcli`
- `t` and `taskcli` are equivalent; they are the canonical entrypoints to the tool.
- `tt` is an alternative entrypoint designed to show a bit more info by default.
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
This library is still in early development and API will continue to rapidly evolve.
If you need a more mature solution, consider using [pyinvoke](https://www.pyinvoke.org/) or Taskfile.dev.

## Prior art and comparison
### pyinvoke
`taskcli` is very similar to pyinvoke, and builds on many of its ideas.

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
YAML has its benefits, but also drawbacks. Refactoring YAML is hard, and it's easy to make mistakes.
A key benefit of the https://Taskfile.dev project is that it ships as a single portable `task` GO binary.

### argh
`argh` is a great library for creating CLI interfaces from python functions.
It can also be used for creating simple tasks.
Similarly to `taskcli` it also builds on top of `argparse` using type annotations and function signatures.
Unlike `argh`, `taskcli` is designed for creating and manaing more complex libraries of reusable tasks.

## Acknowledgements
- The idea for `taskcli` was inspired by Taskfile.dev and `Justfile` projects.
- This library builds on many ideas from the excellent `argh` project. If you like the idea of building CLI interfaces from python function signatures, and don't need the advanced task-like features of `taskcli`, you should check `argh` out.
- `taskcli` library uses `argparse` and `argcomplete` (optional dependency for tab completion).
