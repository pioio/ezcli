# `taskcli` - a library for pragmatic CLI tools

A library for building pragmatic CLI interfaces.

Features:
- simple to use for small scripts.
- powerful enough for more complex tools (argparse-based)
- familiar `argparse` syntax in the `arg` decorator.
- automatically adds "-v|--verbose" flag to all tasks
- automatically adds "-h|--help" flag to all tasks

Heavily inspired by the excellent `argh` library.

## Differences to `argh`
### Registering tasks
In `taskcli` registering tasks takes place via the `@task` decorator
### Parameters without default values
Given a function with a parameter without a default value:
```
def foobar(path)
    print(a)
```

In `argh`, such a function results in
`./tool.py /tmp/somefile`

in `taskcli`
`./tools --path /tmp/somefile`

Rationale:
- This makes it easier to add a default value later, without breaking existing calls
- Arguments without default value should be used rarely. It's prudent to require the user to specify them explicitly via `arg` decorator.


## Acknowledgements
- This library builds on ideas from the `argh` project
- The library uses `argparse` behing the scenes.


# FIXME
- [ ] Text in help output broken - does include task name. We should modify parser's print-usage to include task name
# TODOs
- [ ] also print env vars in help
- [ ] add -v to help
- [ ] support 'help' syntax
- [ ] add auto short flags
- [ ] add "--no-*" versino of bool flags.
- [ ] add default subtask
- [ ] add @task(name)
- [ ] add @task(aliases)
- [ ] add @task(namespace)
- [ ] allow importing tasks from other modules, even with same names
  - [ ] Right now, this will likely break task_data_args[func_name][main_name]
- [ ] Consider support file with functions prefixed with "task_", and use "main" as the default task by default