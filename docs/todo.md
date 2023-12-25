#TODO:
- [x] add `taskcli.extra_args` to get `-- args`
- [ ]
- changing to task file dir also when invoking a function via python. But make it configurable.
- add separattors to task list, or group
  @separator("dev tasks - use)
  def dev():
    fooo
- JSON format
- sort order
- unit tests
- make imports work properly
- groups
- auto-prefix task names with group prefix
- list important first
- soft order
- easy show hidden tasks (-H
- TASKCLI_SHOW_HIDDEN_TASKS
- env vars should map to config
- before/after to run a function only once
- aliases
- listing all tasks in all dirs above, up intil a custom root (configurable)
  - task .

Features:
- hidden tasks: _foobar: use "named" decorator?
- central config
- tags?
- color code the leading *
- diaply arg help when -vvvv used
- list of optional arg names to always hide from listing


# Later
- Include Taskfile

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