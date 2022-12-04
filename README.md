# `taskcli` - a library for utilitarian CLI interfaces

## Overview
`taskcli` is a Python 3 library for creating dense, utilitarian, command line interfaces.
It's backed by `click` as the parameter parsing backend.

## Target usecase
`taskcli` is targetting python scripts exposing large, hierarchical, collections of relatively simple 'tasks'.

In other words, it's targetting scripts which have many possible execution entrypoints, each being a python function, some of which could be grouped in multiple multi-level `task` hierarchies.

`taskcli` allows you to:
- easily explore even most complex hierarchies of the available tasks,
- see their mandatory/optional parameters (color coded to red and blue),
- see the parameter default values,
- see task aliases (yellow), if any.

Example:
```./myscript.py```
![](docs/example-usage.jpg)
```./myscript.py file create content myfile 'my content'```

# Core features
- Aliases:
  - instead of typing `./script file update mtime (...)`,
  - you can type `./script file u m (...)`
  - or even `./script f u m (...)`
- Dense and utilitarian UI (no fluff).
- All-in-one overview of all possible modes of execution - just run the command with no arguments to see:
  - all tasks defined in (or, imported into) a file, along with their hierarchy,
  - all parameters which the tasks accepts (params in red are mandatory),
  - default values of parameters.
- Docstrings are converted to help text.
- Minimal dependencies (only `click`).
- Expressive: full power of `click`


# Interaction with `click`
`taskcli` wraps around `click` in the following way:
- it changes some of `click`'s defaults,
- adds missing functionality (e.g. command aliases),
- changes default help formatting to a more dense and more verbose one,
  more suitable for summarizing all of the tasks in one go.

# Other
`taskcli` was inspired by the following projects:
- [`invoke`](https://www.pyinvoke.org/)
- [`Taskfile`](https://taskfile.dev)
- [`justfile`](https://github.com/casey/just)

Warning: At this point `taskcli` is still in very early dev stages.
As such, its API will be rapidly evolving without much notice.
If you need something more stable, consider `invoke`.

# Installation
```pip install taskcli```
# Usage
## Optional shell function for your ~/.bashrc
```
function t() {
    if [ -f taskfile.py ]; then
        python taskfile.py
    fi
}
```

# Limitations
The target clients of `taskcli` are python scripts containing many different tasks, each
containing relatively small amount of parameters.
The default help/usage output is optimised for this specific use case, by listing all of the
parameters of all of the tasks in one go.
This means that by default, for tasks containing many (10+) arguments,

the help output can get overly verbose.
# Future work
- [ ] if decorators are absent, autogenerate parameters from type annotations of functions.
- [ ] top-level aliases (`./script file abc` instead of `./script a b c`)

# TODOs:
- include basic logging init
- include 'run' and 'sh' commands
- show arg types by default in help
- aliases for tasks and flavors
- consider auto-generating aliases from the first letter of task names and flavors
- optional groups for tasks
