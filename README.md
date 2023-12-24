# `taskcli` - a library for pragmatic CLI tools

A library for building pragmatic CLI interfaces.

Features:
- have one taskcli per module? each set of tasks needs own settings. some settings should take precedence over others.
- simple to use for small scripts.
- powerful enough for more complex tools (argparse-based)
- familiar `argparse` syntax in the `arg` decorator.
- automatically adds "-v|--verbose" flag to all tasks
- automatically adds "-h|--help" flag to all tasks
- accept environment vars to args?
- expect environment? Print it in task list?
-  @task(env=[var1,var2])
- --[no-]confirm - no underscored?
- auto put important tasks in default.

# Later
- Include Taskfile

2023-12-24Heavily inspired by the excellent `argh` library.

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