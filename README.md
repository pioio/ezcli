# taskcli

`taskcli` is a minimalistic Python 3 CLI library for automatically
creating command line interfaces from function signatures which simply work.

Each function annotated with `@task()` is exposed as a command line "task".
Running your script with no arguments will list all available tasks.

It was inspired with `invoke` and `click`.

## Summary
Note: right now, this project is still in early development.

The library is aimed for small to medium projects.
It will never compete with flexibility of argparse or click.
It is, however, extremely easy to get started with.


## Example usage:
### Code
```
#!/usr/bin/env python
from taskcli import task, cli

@task()
def print_message(num: int, message="Hello, World!"):
    """This is my description
    num: number of times to print a messsage, mandatory
    message: message to print, optional
    """
    for x in range(num):
        print(message)

@task()
def add_numbers(number_a: int, number_b: int):
    """This task adds two numbers.
    number_a: first number
    number_b: second number
    """
    print(number_a + number_b)

cli()
```
### Resulting CLI interface


## Core features:
- Minimal dependencies.
- Miminal boilerplate, just add a decorator to your function to trun it into a "task".
- Each task is exposed on the CLI.
- Running the script with no arguments prints the list of available tasks.
- Each function with a simple `@task()` decorator will be added exposed from the cli.
- Parameters are automatically converted to command line flags.
- Docstring are converted to help text.
- Changing function signature does not require changing the attached the CLI code.



# TODOs:
- show arg types by default in help
- aliases for tasks and flavors
- consider auto-generating aliases from the first letter of task names and flavors
- optional groups for tasks
