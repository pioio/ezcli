# `taskcli` - Customization

This document gives an overview to customize `taskcli` to your liking.

## Customizing taskcli

### Customizing `t` and `tt`
By default `tt` is the equivalent of running `t --show-hidden`. But you can change that

In your tasks.py file:

```python
from taskcli import tt
tt.config.default_options_tt = ["--show-optional-args"]
```
