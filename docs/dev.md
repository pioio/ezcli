# `taskcli` - Developer documentation

Internal documentation for developers.

([click here to go the main index](../README.md))

## Working with the code
### Initializing the project
```bash
git clone <url>
cd taskcli
python -m venv venv
source venv/bin/activate
pip install -e .[dev,docs]
```

### IDE settings
- 120 chars line length

### Use `taskcli` to build `taskcli` itself
Run `t` in the root of the project to list all the available tasks.


Some of those will include:
- `t pre-commit`, or `t pc` for short, will run all the pre-commit checks on the current checkout.
- `t test`, or `t t`,  will run all the tests tests.
- and more

See `tasks.py` in the root of the projeft for details

Run `t` in the `docsgenerator/` folder to see the tasks available for generating documentation.
Some of those doc-related tasks are imported to the root `tasks.py` file, so you can run them from there as well.

## Implementation details
### Entrypoint and startup
- The main entrypoint is the `main_internal` function.
- most config (cli/env) options are defined in a config object in one of the files.
- we use this config object build a small initial `argparse` parser to parse flags like `-f`
- we use that to initialize the runtime
- include the main taskfile (one or more), merging them
- include any parent taskfile
- `main_internal` call `dispatch` to proceed with execution.


### Task and Groups
Task needs to have unique `task.name`.

Groups do not have to have unique names. When doing `taskcli group` of a group that a duplicate, we simply print content of both.
This make merging parent to the current context easier, as we don't have to merge parent's group into local ones.

### Logging
Standard Python logging is used, with the exception of extending the `logging.Logger` with a `log.trace()`.
The output of `log.trace` is logged in `-vv` and `-vvv` modes.

### Unit tests and Integration tests:
Using pytest.
`tests/<name>_test.py`  -- tests a specific module (unit)
`test/test_<name>.py` -- tests a collection of modules (integeration)

### Task creation and .include()
Using the @task decorator causes the decorated function to be turned into a `Task` object.
As part of executing the decorator, the new `Task` object gets stored in a special `taskcli`-specific field
in the module which used the @task decorator.

Finally, when `dispatch` runs, it selects the root module, and loads all the Task objects that
are there and copies them
into the runtime context. From which it then lists and executed them.

### Including modules
Combining modules works by a combination of `import` statement and `taskcli.include` function.
- python `import` statements cause the @task decorators in the imported modules to be executed
  (causing the `Task` objects to be created in the special fields in the modules being imported).
- `taskcli.include` function copies the `Task` objects from the module being included into the
  module which is doing the including.

This can happen multiple times, e.g.
-  Modules A imports B, which imports C.
-  Modules B then includes tasks from C into itself
-  Module A then includes tasks from B (including those included from C) into itself

Finally, as described above, the `taskcli.dispatch` simply takes all the `Task` objects from the root
module (e.g. A in the example above), and executes using them.