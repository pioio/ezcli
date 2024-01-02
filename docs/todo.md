# TODOs for `taskcli`

## Short-term TODOs:
- [ ] Make tt.config be on per module basis
- [ ] don't add '.' to namespace
- [ ] unit tests for listing items in group
- [ ] unit test for decorating same name function twice in the same module
- [ ] print (tt.config) not working -> unit test, troubleshootingdoc
- [ ] TODO: early parse should parse env vars (make it a member function of Field? .get_current_value)
- [ ] FIXME: doing `t -f ../../tasks.py TAB` results in wrong tab completion

- [x] add task.__call__  unit tests

- [ ] Remove old 'extra tasks' fields
- [ ] parent_task_filter unit tests
- [ ] Make empty taskfile work for including parents via filter
- [x] tt.include("../../tasks.py", filter=lambda task: task.important) -- relative paths in include should be anchored to the file! Disallow them for now?
- [ ] move building package from taskfile to tasks.py
- [ ] using -f to specify file in other dir still make taskfile be loaded locally, it should skip opening taskfile
- [ ] BUG: dynamic task creation with  'x=x, person_name=person_name' does not allow to set person name from the CLI
- [ ] __init__.py is needed in top project to be bale to import docsgenerator/tasks.py which imports generator ... not perfect
  - [ ] I might need a wrapper for remote-import whcih switches dir and imports the module
- [ ] Test for alias namespace conflicts - silently stripthem?
- [ ] test foo (x:int)   does not have a long flag
- [ ] consider starting any local tasks_X.py file, or at least allow using it for that
- [x] test sys.exit results in proper code being passed to the shell- write out a .py file and run it.
- [ ] loading ./tasks.py from dir above, merging them with the local one.
  - [ ] crashes if added 'dev' section in screenshots/tasks.py
  - [ ] unit-test clash of aliases when merging - do not import aliases in such case
  - [ ] allow preventing merging with the one from above? Or make it explcii?  tt.config.merge_with_parent = False
  - [ ] Namespace added in wrong place: that's `t` in examples/screenshot
    - [ ] included tasks
          included...docs.generate-all-docs ^ i.dgd
          included...docs.test-documentation ^ i.dt
  - [ ] add unit test that it changes to the parent dir of merged in parent file

- [ ] unit test hide-not-ready
- [ ] unit test for error if no tasks detected
- [ ] Module - add custom class to represent module, with my custom per-module fields
- [ ] combine listing with specifying a task
- [ ] unit test for  @task(important=True, format="{name} {clear}{red}(PROD!)")

- [ ] run task binary regardless of taskfile being found or not

- [x] groups and tasks with tags  task -t op, also --show-tags

- [ ]
  - [ ] detect duplicates when including
- [ ] Stop adding '.' to namespace?
- [x] rename namespace to namenamespace
- [ ] FIXME: optional flags are not gray (disk usage example)
- [ ] unit test for duplicate task names
- [x] nesting groups should simply create an indent



## Smart formatting
- [ ] consider auto including important from parent
- [ ] consider ----[ parent/path/to/tasks.py ]----------------- in the separator to make it clear where it came from.
- [ ] trim the summary if too wide
- [ ] if no parent, but main task is above, also print a line
  - [ ] -------[  (..)folder/parent/tasks.py         ]----
  - [ ] -------[  (..)folder/parent/foo/foo/tasks.py ]----


## Long-term TODOs:
- [ ] auto split columne
- [ ] detect pipe to grep, and prefix lines with group name
- [ ] pre/post hooks, also pre_if, post_if
- [ ] Render first parent grouptask, then HR separatro, than normal groups?
- [ ] add --color yes/no -- finish screenshot generation
- [ ] Store config on per module level? Otherwise including a file which messes with the global config might reset our changes.
- [ ] Allow auto-including taskfile via env vars, e.g. to share private tasks between projects
- [ ] ability to include modules while preserving group info (merge=True)
- [ ] Logging which does not interfere with other librarie
- [ ] central project.py which allow to share tt.config between subfolders?
- [ ] add --mode|-m, which would permamently change options which are being shown, using tags
  - [ ] t -m imp,users,infra
- [ ] unit tests for main
- [ ] unify how Tasks and Groups are stored. Groups are in `groups._stacks`. Tasks are in module.
- [ ] allow to rename tasks when including
- [ ] auto-load files with _tasks.py in them? define pattern via regex?
- [ ] arg help from docstring
- [ ] docs: mark prop field as important, to create a separate docs section with them
- [ ] wrap right column text, for screenshots
  - [ ] # TODO: have task have internal sort key, combination of digit + name for easier sorting
- [ ] Run doc generation in the doceker container (this will allow showing merged/extra task examples)
- [ ] def lint(paths: Paths), with Paths having a default -- Cannot call from CLI without the path
  - [ ] Should a default be added to the function?
- [ ] consider 'f' as entrypoint
- [ ] Settings page - highlight important switches
- [ ] argparse add_argument_group
- [ ] print warning if TASKCLI env var is set which is not known
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
- [ ] allow one task to be in more than one group - add unit tests
- [ ] ctx manager for changing env
- [x] Include Taskfile
- Improve config system - use field's doctstring to fill out the help field in ConfigField, and then run _add_boola utomatically
    self.field_hide_not_ready = ConfigField(False, "hide_not_ready",  help=f"Tasks which are not ready to run (e.g. due to missing env vars) will be automatically marked as hidden.")
    self.hide_not_ready: bool = False
    """Docstring"""
    ...

----------
keep track of current group on per module level.



