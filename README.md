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

## Installation

```
pip install taskcli
```

## Example usage:
### Code
```
#!/usr/bin/env python
from taskcli import task, cli

@task()
def print_message(num: int, message="Hello, World!"):
    """Print a simple message "-n|--num" number of times.

    num: the number of times to print the messsage, mandatory (can also use '-n).
    message: The message to print, optional, can also be redifined with '-m'.
    """
    for x in range(num):
        print(message)

@task()
def add_numbers(a: int=2, b: int=2):
    """Adds two numbers
    a: first number
    b: second number
    """
    print(a + b)

if __name__ == "__main__":
    cli()

```
### Run it
    ./example.py -h
    or
    ./example.py -hh  # for more detailed help

### Resulting CLI interface
```
print-message        Print a simple message "-n|--num" number of times.
         -n|--num
        [-m|--message]       Default: Hello, World!


    num: the number of times to print the messsage, mandatory (can also use '-n).
    message: The message to print, optional, can also be redifined with '-m'.

add-numbers          Adds two numbers
        [-a]                 Default: 2
        [-b]                 Default: 2

    a: first number
    b: second number
```

### Run the task
```
./example.py add-numbers -a 2 -b 3
```

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
