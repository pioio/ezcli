
- [x] Include from module by filter

- [x] mark included task with^
- [x] task init is broken

- [ ] optional flags are not gray (disk usage example)
- [ ] hide_not_ready unit test

- [x] test init.py
- [ ] unit test hide-not-read
- [ ] Module - add custom class to represent module, with my custom per-module fields
- [ ] unit test: searching by tag should show hidden tasks, samel ike showing a group - unit
- [ ] unit test- broken get hidden
- [ ] reduve -v noise

- [ ] make .include return included tasks
- [ ] allow showing tasks in hidden groups?
- [ ] nice warning if no tags listed
- [ ] separate defaults for tt mode on per fiel basis
- [ ] unit test for searching when some matching tasks are hidden
- [ ] unit test for error if no tasks detected
- [ ] combine listing with specifying a task
- [ ] tt should have bigger tab completion than t
- [ ] proper typed interface to @task
- [ ] make metavar work in task list
- [ ] unit test for   @task(important=True, format="{name} {clear}{red}(PROD!)")

- [x] make type work with user defined functions
- [x] add unit test for args passed to argparse from 'arg'
- [x] aliases unit tests
- [x] coverage
- [C] run task binary regardless of taskfile being found or not
- [ ] show again number of tasks in group (not shown now)
- [ ] show which group has hidden tasks
- [ ] mark hidden gorups as (hidden)
- [ ] list hidden group in one line at the end
- [ ] denote included tasks, somehow, e.g. with a star suffix, or "^ prefix in summary
- [ ] allow imported function to chdir to the local dir?
- [x] groups and tasks with tags  task -t op, also --show-tags
- [ ] using -f to specify file in other dir still make taskfile be loaded locally
- [x] task -L should show ALL info
- [x] add auto conversion to int/float from string
- [ ] task .dev   to list item in group, including hidden groups
- [ ] groups having unique namespace
- [ ] task op
- [ ] examples: parts "call with" in docstring and try to call the example with that
- [ ] extend with a c
- [ ] groups having namespacesby default, but optionally not  Group(ns=False)
  - [ ] always print group, but if ns is optional, print it dimmed ou
- [ ] Make bools works when no type present.
- [ ] allow one task to be in more than one group?
- [ ] allow certain tasks in group to not be namespaced?
- [ ] Make sure importing a module does not add its tasks to the global default group by default
- [ ] *args and **kwargs support and unit tests

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
  - [ ] include in tasks.py still broken
    - [ ] def xxx():
            pass

        include(xxx)

- [ ] unit test for duplicate task names
- [ ] nesting groups should simply create an indent

#### groups
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


# Long-term TODOs
- [ ] will setting a tt.config.foobar in a imported module overwrite the global one? should we have tt.config.reset() to call after imports are done?
- [ ] run: print the task being run,, along with a chain of calls, but only when running via taskcli
- [ ] chaining tasks  `taskcli task1 task2`
- [ ] pre/post hooks
- [ ] --hide-regexp
- [ ] add default task
- [ ] make "t gr*oof" auto enter search mode - will require custom argparse validator
- [ ] `t -S` to search through docstrings, include matching line?
- [ ] ability to exclude certain arguments from parser (task(exclude)), the arg must have a default)
- [ ] tt.set_overview for the entire taskfile. This will require storing overview on per-module basis (or storing it only for current one), and loading
- [ ] JSON output format
- [x] Include Taskfile
- Improve config system - use field's doctstring to fill out the help field in ConfigField, and then run _add_boola utomatically
    self.field_hide_not_ready = ConfigField(False, "hide_not_ready",  help=f"Tasks which are not ready to run (e.g. due to missing env vars) will be automatically marked as hidden.")
    self.hide_not_ready: bool = False
    """Docstring"""
    ...
