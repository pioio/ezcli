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
def simple_function1(arg1: int=1, arg2: int = 2, arg3: str= "foobar"):
    """This function does foo"""
    log.info("This is a simple function")


@task()
def another_function2():
    log.info("This is another function")


cli()
