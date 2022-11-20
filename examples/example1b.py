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
def add_numbers(a: int = 2, b: int = 2):
    """Adds two numbers
    a: first number
    b: second number
    """
    print(a + b)

if __name__ == "__main__":
    cli()
