#!/usr/bin/env python

import logging

from taskcli import task, cli, flavor

log = logging.getLogger(__name__)
import common

common.setup_logging()

# @flavor("use 42 as argument", arg2=42)


@task(
       flavors=("foo", {"arg1": None, "arg2": 42, "arg3": "foobarccc"}),
)
def foobar(arg1: int, arg2, arg3: str = "foobar"):
    """This function does foo
    this is more docstring
    and even more
    int: xxx
    arg2: zzz"""
    log.info("This is a simple function")

@task()
def barbaz(num_objects: int = 4):
    log.info(f"This is a simple function - barbaz {num_objects}")

import os
@task()
def example_task():
    log.info("This is another example task")
    # run shell
    os.system("echo 'hello world'")


@task()
def perform_task():
    """This one does a thing"""
    log.info("foobar")


cli()
