Required TODO:
- [x] add `taskcli.extra_args` to get `-- args`
- [x] add "-f" to specify the file
- [ ] add "--no-*" version of bool flags.
- [ ] list[bool]  ? list[other-type]
- [x] tuples
- [x] list with no types
- [x] list|None
- [x] param.type.is_bool
- [ ] add unit tests with "-" task names
- [ ] add unit test for args passed to argparse from 'arg'
- [ ] aliases unit tests
- [ ] coverage
- [ ] ability to exclude certain arguments from parser (task(exclude)))

- [ ] run task binary regardless of taskfile being found or not
- [ ] Make unit test use standard formatting for listing.
- [ ] show again number of tasks in group (not shown now)
- [ ] left-align first argument
- [ ] add tests that invoke tasks with arguments
- [ ] show which group has hidden tasks
- [ ] list hidden group in one line at the end
- [ ] denote included tasks, somehow, e.g. with a star suffix, or "^ prefix in summary
- [ ] allow imported function to chdir to the local dir?
- [ ] mark hidden gorups as (hidden)
- [ ] groups and tasks with tags  task -t op, also --show-tags
- [ ] using -f to specify file in other dir still make taskfile be loaded locally
- [ ] include
- [x] task -L should show ALL info
- [x] add auto conversion to int/float from string
- [ ] task .dev   to list item in group, including hidden groups
- [ ] groups having unique namespace
- [ ] task op
- [ ] extend with a c
- [ ] groups having namespacesby default, but optionally not  Group(ns=False)
  - [ ] always print group, but if ns is optional, print it dimmed ou
- [ ] Make bools works when no type present.
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
  - [ ] detect duplicates
  - [ ] task ... task --foo
  - [ ] include in tasks.py still broken
    - [ ] def xxx():
            pass

        include(xxx)
- [ ] FIXME: broken 'task ruff src'
- [x] Aliases
- [x] -L list all
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
- auto-prefix task names with group prefix if ns=True
- print group name on the same line as task, dimmed out, but don't require it
- list important first
- TASKCLI_SHOW_HIDDEN_TASKS
- env vars should map to config
- before/after to run a function only once
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
- dict type, accepting key=value, or json
- [ ] tt.set_overview, this will require storing overview on per-module basis (or storing it only for current one), and loading
- ability to customize the parser with custom flags
  - @task(customize_parser=lambda parser: parser.add_argument('--foo')
    then taskcli.get_args() would return the parsed argparse namespace
- show missing env vars in task list
- JSON format
- Include Taskfile
- converting list[int] from str to list of ints
- add to groups based on tags?
- [ ] Tags
  - [ ] list tasks based on tags
  - [ ] auto add tags based on argument nam or task regex, or envvars
  - [ ] decorate tags based on tags

# FIXME
- [ ] Text in help output broken - does include task name. We should modify parser's print-usage to include task name

# TODOs

- [ ] also print env vars in help
- [ ] add -v to help
- [ ] support 'help' syntax
- [ ] add auto short flags
- [ ] add default subtask
- [ ] allow importing tasks from other modules, even with same names
  - [ ] Right now, this will likely break task_data_args[func_name][main_name]
- [ ] Consider support file with functions prefixed with "task_", and use "main" as the default task by default