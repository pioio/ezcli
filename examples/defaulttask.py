#!/usr/bin/env python3
from taskcli import arg, invoke, task


@task
def hello(foobar: int = 10):
    print("Hello World!!")


invoke()
