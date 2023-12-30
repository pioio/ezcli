# Taskcli

A `t` CLI tool for **fast**, real-life, task automation for fans of the Linux command shell.
Create snappy, powerful, and testable CLI interfaces from simple Python functions.

Manage and automate any project (not only Python) with ease.



## Key features
- Aliases, namespace, groups
- You can group, highlight, tag, hide, list, regex-search your tasks.
- Import and reuse tasks from other modules/dirs  (`tt.include(module_name)`). Directories will be switched automtically as needed.
- Auto hide tasks which are not ready to be run (e.g. due to missing env vars) (`tt.config.hide_not_ready = True`)
- Quickly see the overview of all the tasks, along with optional and mandatory arguments.
- Customize the way your tasks are listed. Customize it on per-project basis, or globally for many projects.
- simple to start, but power and suitable for managing larger projects.
- Automatically switch directories when running tasks imported from other directories (can be disabled).

## Docs overview
[Configuration Settings](settings.md)



## Quickstack
Install:
`pip install taskcli`
`taskcli --init`

Then, all you need is a `tasks.py` file with a single simple function:


## To enable tab completion
Install `argcomplete` package. It's an optional dependency of `taskcli`

Add this to your `.bashrc`
```
eval "$(register-python-argcomplete taskcli)"
eval "$(register-python-argcomplete tt)"
```

## Installation and basic usage
```
# Install the package
pip install taskcli

# Create a ./tasks.py file in the current directory with example content
taskcli --init

# list the tasks in tasks.py
taskcli <task_name>

# Instead of `taskcli` you can also use the `t` script, eg:
t <task_name>
```



## Types of Tasks
All tasks are defined with `@task` decorator
A task can be important, hidden, both, or neither,
e.g.
`@task(hidden=True)`
`@task(important=True)`


Hidden tasks are not shown by default by `t`. Use `tt` to show also them.
Hidden tasks that are meant to be run relatiely inferequently.

Hidden tasks can be listed either by
- with `--show-hidden|-H` flag, or with `--list-all|-L` flag
- or by listing all tasks in specific group.

Important tasks are just that, important.
The reason depends on the cotext.
Important tasks have a special formatting (customizable), and are by default floated to the top of their group.

### Tasks and groups
Each task is always in one specific group.

## Typical usage
- run `t` to list all the (not hidden) tasks in local `./tasks.py` file. Some info is hidden from this overview.
- run `t <task_name>` to run a task.
- run `t <group_name>` to list only tasks in that group. This view includes more detailed info than the full listing.

The goal of `t` is to get a quick overview of all the tasks.
You can always include `t -L` to view all the info for all the groups. But note that for large projects
this can result in a lot of output

## Listing tasks
- `t` is equivalent to `t --list|-l` -- only shows mandatory and important parameters.
- `t -ll` lists tasks in more detail  -- includes all parameter, even optional ones.
- `t -lll` list tasks in even more detauls -- include all parameters, shows default values of optional parameters.
- `t -L` show all info - can be very verbose


## Main features
- Optimized for fast startup (majority of startup time is python interpreter startup). Benchmark with `TASKCLI_ADV_PRINT_RUNTIME=1`
- Easy to start, flexible when needed (access to underlying `argparse` parser)
-

## Other features
- Expose regular python function into a task, print their output to stdout  (`-P` flag.)

- Integration with go-task (http://taskfile.dev).  If `TASKCLI_GOTASK_TASK_BINARY_FILEPATH` is set, any local Taskfile.yaml files are loaded automatically.

- Support for exotic parameters types. Parameters with types which cannot be converted from argparse will be gracefully ignores (so long as they have a deafult value). Future work: support for custom conversion functions.

## Customisation
`taskcli` comes with sane defaults out of the box, but it can be

### Customize Argparse parser
TODO: see cookbook


### Make certain tasks stand out by marking them as important
```
@task(important=True)
def do_something():
    ...
```

### Hide tasks from default listing
```
@task(hidden=True)
def do_something():
    ...
```

### Customize the way tasks are listed, e.g. add a red "prod!" suffix to some
```
prod_warning = "name {red}(production!){clear}"
@task(format=prod_warning)
def do_something():
    pass
```

### other
- customize default formatting string
- ...

## Design consideration
- `taskcli` shows if your env is ready to run a task. Many tasks need special env variables set.
   It's useful to see at a glance which tasks are ready to run, and which are not.
   Specify either env var names, or  for advanced cases, a function that returns a string.

## Roadmap
- Custom env validation functions





## FAQ
Q: why no namespace by default?
A: in most cases it just requires additional unnecessary keystrokes. If you feel you need namespaces, you can add them manually.

## Automatic Directory switching

By default running a task will switch to the directory where the task is defined.
This happen both when you run the task via `taskcli`, and when you call the python function decorated with `@task` yourself.
The section below outlines how that works.
Note, `@task(change_dir=False)` will disable this behavior, and preserve whatever CWD was set right before the task function was called.

See `TASKCLI_EXTRA_TASKS_PY_FILENAMES` to customize where `taskcli` looks for `tasks.py` files in directories above the current one.




### Simple project
project/
- tasks.py                # let's say this one haas 3 tasks
    * upload-files
    * deploy-to-prod
    * deploy-to-staging

Those 3 actions are available anywhere within the `project/` dir tree.
This mean you can run
$ project/foo1/foo2/foo2 $ t deploy-to-prod
without needing to switch to the root of the project first.

### Advanced project
```
project/
- tasks.py     # let's say this one has the same 3 task, and one new included one.
    * upload-files
    * deploy-to-prod        # tagged as "important" within this file
    * deploy-to-staging
    * bake-cake             # included by name from  project/foo/bakery/tasks.py


project/foo/bakery/
- tasks.py                 # chooses to auto-include all 'important' tasks from project/tasks.py
    * bake-cake            # defined here, running it from anywhere switches to project/foo/bakery/
    ⬆ deploy-to-prod      # auto-included from project/tasks.py, running it switches to project/ dir


For example, running
project/some/other/directory $ t bake-cake
will find the task in project/tasks.py , notice it was imported from project/foo/bar/tasks.py,
will switch to project/foo/bar/ dir, and run the task in there
```