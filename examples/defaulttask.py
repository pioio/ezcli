#!/usr/bin/env python3
from taskcli import arg, task, cli

@task
def hello(foobar:int=10):
    print("Hello World!!")



cli()