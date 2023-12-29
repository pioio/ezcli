# Dev documentation

Internal documentation for developers.


## Task creation and .include()
Using the @task decorator causes the decorated function to be turned into a `Task` object.
As part of executing the decorator, the new `Task` object gets stored in a special `taskcli`-specific field
in the module which used the @task decorator.

Finally, when `dispatch` runs, it selects the root module, and loads all the Task objects that
are there and copies them
into the runtime context. From which it then lists and executed them.

## Including modules
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