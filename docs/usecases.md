# `taskcli` Usage patterns

At its heart, `taskcli` is a tool for creating CLI entrypoints to your tasks (any tasks, any project)



There's many ways in which you can use `taskcli`.

This section discusses things like
- using `taskcli` for managing automation tasks.
- using `taskcli` for projects of varying sizes (from tiny to large).
- using `taskcli` to create a new, overarching, view to multiple separate projects.

([click here to go the main index](../README.md))

## Tiny project
The simplest scenario:
- A single `tasks.py` containing both your task (i.e. the entrypoint defining the CLI) and the logic behind it.
- All tasks are visible by default when running `t`.
- Some tasks might be, optionally, marked as 'important'; this will make them stand out in the list of tasks.

This could be small a sofware project where you need the typical sets build/test/ship tasks.

Or, it can be just a small collection of small unrelated automation tasks, like 'check-weather', 'brew-coffee', 'check-email', etc.


## Tiny project with hidden tasks
Another simplest scenario:
- A single `tasks.py` containing both your task and their logic.
- Not all tasks are visible by default for the `t` command -- some tasks (or groups of tasks) are hidden.
- you can use `tt` to show the hidden items. (`tt` == `t --show-hidden`)

Useful when you typically only ever run small subset of tasks (e.g. `build-test-deploy()`), but still want to keep
the other ones (`build()`, `test()`, `deploy()` around and easily accessible in case they are needed.



## Small project
- Still a single `tasks.py` containing all the Taskk.
- Some logic might be in separate python files/modules imported with Python's `import` statement. This helps keep the `tasks.py` file small and readable. Those file could be co-located in the same subdirectory as the main `tasks.py`, or be in subdirectories.
- Some tasks might be hidden, and are not shown by default. You can use `tt` to show them.
- Some tasks might be marked as `important`, to make them stand out in the task list.
- Some other related tasks might be grouped into groups (to easily find related ones). Groups can be nested.
- Some tasks might have tags assigned to them, to easily show e.g. all the tasks related to a specific topic.

Your directory structure could be a collection if standalone files, or part of a bigger python package

## Use taskcli as a view into several other projects
In this scenario you have mutliple distinct projects, some usings tasks.py each in their own own, some not using it all.k

You then create a separate `taskcli` which imports and includes select tasks from all of them. Possibly adding some custom tasks.
For projects which don't use tskcli, you create new Task which forward the calls to the other projects scripts via the shell.

This gives you a single point of entry for all of the included projects.
This works exceptionally well since Tasks automatically change directories to wherever they are defined.

(This way, when writing task for a project, you don't have worry about from where, relative, the task will be called.)

## tasks.py alongside a Python package
Unlike other patterns, this one is specific to Python projects.

In this case you have a repo with one, or more, python packages, and a tasks.py which might, or might not be, part of the package.

The tasks.py could depend on (import) the package (or not). You can then use `tasks.py` to have tasks that e.g. build and test your package. And some tasks which actually import it, and use it.

This pattern is useful if your tasks require a lot of custom logic. You can put that logic inside of the package (even if you don't mean to ever ship it), and then have tasks.py `pip install -e .` it, import it, and  use it.

Alternatively in theory you could:
- have one tasks.py to build/test/dev-work on your package
- another (set of) tasks.py file(s) that are part of your package, which be installed along with it. Though sometimes in this case what you need is not a `tasks.py` that glues together functions,  but rather a bespoke CLI app.


## Medium-size project importing other tasks, without including them

```
import subproject

@task
def build_and_test():
    subproject.build()
    subproject.test()
```
- This project imports tasks from a python (sub)module, without exposing them.
- The `build` and `test` tasks are defined in `subproject/tasks.py` file.
- The main tasks.py file has only one task, "build_and_test", which forward the calls internally.
- Because `build` ad `test` are `@task`, calling them switches the current working directory to wherever they are (unless `change_dir=False` was used).

## Medium-size project importing as well as including (exposing) other tasks
```
import subproject

tt.include(subproject)

@task
def build_and_test():
    subproject.build()
    subproject.test()
```
In this case the main `tasks.py` will report three tasks:
- `build_and_test`,
- `build`,
- `test`.

Here, you can even choose to not have any tasks defined in the main `tasks.py` at all,
and only ever exoise tasks included from other files.


## Large project
Similar to Medium projects, but you now have multiple python files containing Tasks.

Those taskfiles can:
- each be in a separate subdirectory (as `tasks.py`)
- share some directories under unique names (use `t -f filename.py` to run them)

You can choose to import some of those tasks to a central `tasks.py` (e.g. in the topmost directly), and have them be show them there.

Furthermore, on top of tasks spread in individual tasks file, you can choose to
- not have any central (main) `tasks.py`, and thus access all tasks via the files they are defined in, or
- have a central `tasks.py` file which imports (and possibly includes) some/all of the tasks from other tasks.py files. All the while possibly hiding some of those in the default task listing view, only keeping the most important one.

Example:
```
tasks.py    # run via `t`, main tasks py, imports+includes from other files
build.py    # run via `t -f build.py`
deploydir/tasks.py    # run via `t -f deploydir/tasks.py`
```


## Multi-project systems
For example, given multiple loosely related projects
```
/home/user/project1/tasks.py
/home/user/project1/subdir/othertasks.py
/home/user/project2/tasks.py
/etc/project2/tasks.py
/var/lib/project3/moretasks.py

```

You can combine those project into a single view.
You could import and include all the tasks, but typically you will want to filter them in some way.
```
from taskcli import tt
from subdir import othertasks
tt.include(othertasks)
tt.include("/home/user/project2/tasks.py", filter=lambda task: task.important)
tt.include("/var/lib/project3/moretasks.py", filter=lambda task: task.name.startswith("deploy"))
tt.include("/etc/project2/tasks.py", filter=lambda task: "foobar" in task.tags)
```

## Future work: Sharing tasks.py via git/http/ssh
Download and inluding tasks.py from remote systems, including over SSH (cached locally).
Running a task will SSH to that system to invoke the task.


## Merging multiple `tasks.py` files
TODO( needs work)
- After finding `tasks.py` , the tool imports it.
- if `-p` was used,

- You can use `tt.include_parent(filter=my_filter_function)` to customize which tasks are merged in.
```python
from taskcli import tt

def my_filter_function(task):
    return task.name.startswith("deploy") or "prod" in task.tags

tt.include_parent(filter=my_filter_function)
```


This allows you to have a single `tasks.py` file in the root of your project, and then have additional `tasks.py` files in subdirectories, and have them all be merged together any way you like as you traverse the directory tree.
