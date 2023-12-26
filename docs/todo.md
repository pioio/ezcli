#TODO:
- [x] add `taskcli.extra_args` to get `-- args`
- [ ] include
- [ ] task script
- [ ] show num of hidden groups
- [ ] task -L should show ALL info
- [ ] hidden tasks
- [ ] advanced tasks
- [ ] TODO custom format
- [x] add auto conversion to int/float from string
- [ ] task .dev   to list item in group, including hidden groups
- [ ] groups having unique namespace
- [ ] task op
- [ ] extend with a c
- [ ] groups having namespacesby default, but optionally not  Group(ns=False)
  - [ ] always print group, but if ns is optional, print it dimmed out
- [ ] allow one task to be in more than one group?
- [ ] allow certain tasks in group to not be namespaced?
- [ ] Make sure importing a module does not add its tasks to the global default group by default
- [ ]
  - [ ] per module task list
  - [ ] include(child_tasks.child1)
  - [ ] include to group
  - [ ]
  - [ ] add warning if function name overwridden
  - [ ] include(group, newgroupname)
  - [ ] include(group.task, new-task-name-in-current-group)
  - [ ] include not decorated function
  - [ ] A includes B, B includes A
  - [ ] task ... task --foo
  - [ ] include in tasks.py still broken
    - [ ] def xxx():
            pass

        include(xxx)
- [ ] FIXME: broken 'task ruff src'
- [ ] Aliases
- [ ] -L list all
- [ ] task --init <filename> to create a stub task file
#### groups

Each task has one namespace,
foo.bar.ns.task
Typing namespace can be optional

Each task has tags

task groupped based on tags

group desc should say how many hidden tasks there are




- groups in the order they were defined
  - tasks in a group in the order in which they wer eadded
- changing to task file dir also when invoking a function via python. But make it configurable.
- add separattors to task list, or group
  @separator("dev tasks - use)
  def dev():
    fooo
- sort order
- unit tests
- groups
- auto-prefix task names with group prefix if ns=True
- print group name on the same line as task, dimmed out, but don't require it
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
- ability to customize the parser with custom flags
  - @task(customize_parser=lambda parser: parser.add_argument('--foo')
    then taskcli.get_args() would return the parsed argparse namespace
- show missing env vars in task list
- JSON format
- Include Taskfile
- converting list[int] from str to list of ints
- add to groups based on tags?

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