# `taskcli` - Customization

This document gives an overview to customize `taskcli` to your liking.

([click here to go the main index](../README.md))

## Customizing taskcli

### Customizing `t` and `tt`
By default `tt` is the equivalent of running `t --show-hidden`. But you can change that

In your tasks.py file:

```python
from taskcli import tt
tt.config.default_options_tt = ["--show-optional-args"]
```

Or, do this to also always show tasks from the first parent (one or more dirs up) taskfile.
Effectively, this will force `t` to combine the content of the task file in the current directory (eg `/home/users/project/foo/bar/tasks.py`), with the first
task file above it (eg `/home/user/project/tasks.py`).
```python
from taskcli import tt
tt.config.default_options_tt = ["--show-optional-args", "-p"]
```
