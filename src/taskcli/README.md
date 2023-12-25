TODO:
- changing to task file dir also when invoking a function via python. But make it configurable.
- add separattors to task list, or group
  @separator("dev tasks - use)
  def dev():
    fooo
- JSON format
- sort order
- unit tests
- make imports work properly
- groups
- auto-prefix task names with group prefix
- list important first
- soft order
- easy show hidden tasks (-H
- TASKCLI_SHOW_HIDDEN_TASKS
- env vars should map to config
- before/after to run a function only once
- aliases

Features:
- hidden tasks: _foobar: use "named" decorator?
- central config
- tags?
- color code the leading *
- diaply arg help when -vvvv used
- list of optional arg names to always hide from listing

Bugs:
    ARG1,ARG2=zzz,ARG3OPTIONAL=xxx,KW=3
FullArgSpec(args=['arg1', 'arg2', 'arg3optional', 'kw'], varargs=None, varkw=None, defaults=('zzz', 'xxx', 3), kwonlyargs=[], kwonlydefaults=None, annotations={'arg1': <class 'str'>, 'arg2': <class 'str'>, 'arg3optional': <class 'str'>, 'kw': <class 'int'>})


## Include
check all dirs up to the parent,
try to include tasks.py from a chain of parent dirs, under ..

*** some group
* task1
* task2

*** soe other group
* task3
* task4

*** [..]prent-group1
* parent1
* parent2

*** [...]parent-group2
* parent1

..paren

parent taskfile must explicly agree
taskfile.settings.include_parent_from_children = True
taskfile.settings.group_to_show_in_children = [] # all

task -l
echo 'parent task available, use -ll to show'
task ...parent-group1.parent1