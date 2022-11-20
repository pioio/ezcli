# Taskcli
A CLI library for creating comprehensive command line interfaces
from function signatures.

Right now, this project is still in very early development.


# example usage output

## For simple
task-name            A short description of the task
        [--option-name]       default: 42
        --another-option      (madatory)

    Long description of the task from docstring.

## For complex examples
task-name            A short description of the task
    (default)         (the "default" string does not have to be specified). If there's no flavor, don't print the default
        [--option-name]         default: 42
        [--another-option]      default: /some/path

    flavor-name      A short description of the flavor
        [--option-name|-o]       default: 1
        [--another-option|-a]    default: /some/path

    other-flavor
        --option-name|-o         (mandatory)
        [--another-option|-a]    default: /some/yet/other/path

    Long description of the task from docstring

    Examples:
        task-name --option-name 1 --another-option /some/path
        task-name flavor-name --option-name 1 --another-option /some/path
        task-name other-flavor --option-name 1 --another-option /some/path

# TODOs:
- show arg types by default in help
- aliases for tasks and flavors
- consider auto-generating aliases from the first letter of task names and flavors
- optional groups for tasks
