

- [ ] def lint(paths: Paths): Cannot call from CLI without the path

- [ ] move building from taskfile to tasks.py
- [ ] code location of merged module is wrong @ coverage report (/Users/p/code/mygithub/taskcli/taskcli_import_dribzrel.py:36)
- [ ] loading ./tasks.py from dir above, merging them with the local one.
  - [ ] unit tests for merging tasks
  - [ ] cleanup main
  - [ ] How to handle A importing B, importing A?
  - [ ] t .  # list only tasks from local dir
  - [ ] crashes if added 'dev' section in screenshots/tasks.py
  - [ ] # TODO: have task have internal sort key, combination of digit + name for easier sorting
  - [ ] rename 'filter' to filterfun?
  - [ ] unit-test clash of aliases when merging - do not import aliases in such case
  - [ ] t .. # list only one level (not dir) up
  - [ ] would have to use importlib, tried it once, but is tricky. Maybe not worth it
  - [ ] allow preventing merging with the one from above? Or make it explcii?  tt.config.merge_with_parent = False
  - [ ] Namespace added in wrong place: that's `t` in examples/screenshot
    - [ ] included tasks
          included...docs.generate-all-docs ^ i.dgd
          included...docs.test-documentation ^ i.dt
  - [ ] add unit tests
  - [ ] fix time keeping in main()
  - [ ] add unit test that it changes to the parent dir of merged in parent file
  - [ ] marke the ones from the parent, sort separtely to first?
    - [ ] add separator between them?
    - [ ] tt.config.merge_parent_filter = lambda task: task.name.startswith("parent_")


- [ ] hide_not_ready unit test
- [ ] --init still not working - add unit test
- [ ] unit test hide-not-read
- [ ] Module - add custom class to represent module, with my custom per-module fields
- [ ] unit test: searching by tag should show hidden tasks, samel ike showing a group - unit
- [ ] unit test- broken get hidden

- [ ] unit test for searching when some matching tasks are hidden
- [ ] unit test for error if no tasks detected
- [ ] combine listing with specifying a task
- [ ] unit test for  @task(important=True, format="{name} {clear}{red}(PROD!)")
- [ ] allow one task to be in more than one group - add unit tests
- [ ] run task binary regardless of taskfile being found or not

- [x] groups and tasks with tags  task -t op, also --show-tags
- [ ] using -f to specify file in other dir still make taskfile be loaded locally

- [ ]
  - [ ] per module task list
  - [ ] include(child_tasks.child1)
  - [ ] include to group

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
- [ ] Stop adding '.' to namespace?
- [ ] rename namespace to namenamespace
- [ ] FIXME: optional flags are not gray (disk usage example)
- [ ] FIXME: doing `t -f ../../tasks.py TAB` results in wrong tab completion
- [ ] unit test for duplicate task names
- [x] nesting groups should simply create an indent




# Long-term TODOs
- [ ] Settings page - highlight important switches
- [ ] argparse add_argument_group
- [ ] print warning if TASKCLI env var is set which is not known
- [ ] pre/post hooks
- [ ] list of optional arg names to always mark as important?  add imperative, as Cookbook example.
- [ ] hidden tasks: _foobar: use "named" decorator?
- [ ] interactive confirmaiton before running a task (confirm only once)
- [ ] allow imported function to chdir to the local dir (i.e. allow setting explicit working dir for any task, including imported ones)
- [ ] examples: parts "call with" in docstring and try to call the example with that
- [ ] tt should have bigger set of tab completion than t
- [ ] --show to show a specific group or task in full detail
- [ ] make metavar work in task list
- [ ] tags for groups
- [ ] will setting a tt.config.foobar in a imported module overwrite the global one? should we have tt.config.reset() to call after imports are done?
- [ ] run: print the task being run,, along with a chain of calls, but only when running via taskcli
- [ ] chaining tasks  `taskcli task1 task2`
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
