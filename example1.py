#!/usr/bin/env python
from taskcli import task, cli

@task
def simple_function():
    print("This is a simple function")

simple_function()
cli()
