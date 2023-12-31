# TODOs for `taskcli`

## Short-term TODOs:
- [ ] structure
- [ ] add --color yes/no -- finish screenshot generation
- [ ] rename tasks when including
- [ ] print (tt.config) not working

- [ ] add task.__call__  unit tests
- [ ] t shows hidden tasks
- [ ] tt.include("../../tasks.py", filter=lambda task: task.important) -- relative paths in include should be anchored to the file! Disallow them for now?
- [ ] BUG: dynamic task creation with  'x=x, person_name=person_name' does not allow to set person name from the CLI
- [ ] wrap right column text, for screenshots
- [ ] use "import_module" instead of "include" ?
- [ ] __init__.py is needed in top project to be bale to import docsgenerator/tasks.py which imports generator ... not perfect
  - [ ] I might need a wrapper for remote-import whcih switches dir and imports the module
- [ ] need more unit tests for imports in various file dir sructures
-
- [ ] test foo (x:int)   does not have a long flag
- [ ] consider starting any local tasks_X.py file, or at least allow using it for that
- [ ] test sys.exit results in proper code being passed to the shell- write out a .py file and run it.
- [ ] move building from taskfile to tasks.py
- [ ] test nargs=4 works
- [ ] example - standardize on t vs taskcli
- [ ] code location of merged module is wrong @ coverage report (/Users/p/code/mygithub/taskcli/taskcli_import_dribzrel.py:36)
- [ ] loading ./tasks.py from dir above, merging them with the local one.
  - [ ] unit tests for merging tasks
  - [ ] cleanup main
  - [ ] circular imports, prevent duplicates gracefully
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
- [ ] auto-load files with _tasks.py in them? define pattern via regex?

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




## Long-term TODOs:
- [ ] Run doc generation in the doceker container (this will allow showing merged/extra task examples)
- [ ] def lint(paths: Paths), with Paths having a default -- Cannot call from CLI without the path
  - [ ] Should a default be added to the function?
- [ ] consider 'f' as entrypoint
- [ ] Settings page - highlight important switches
- [ ] argparse add_argument_group
- [ ] print warning if TASKCLI env var is set which is not known
- [ ] pre/post hooks
- [ ] t --env - print bash env of the project, e.g. tcd -> goes to project t --env
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
