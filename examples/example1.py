#!/usr/bin/env python

import logging

from taskcli import task, cli, flavor

log = logging.getLogger(__name__)
import common

common.setup_logging()

#@flavor("use 42 as argument", arg2=42)
@task(
    flavors=("foobar-flavor", {"arg2": 42}),
)
def simple_function(arg1: int = 1, arg2: int = 2):
    """ This function does foo"""
    log.info("This is a simple function")


@task
def another_function():
    log.info("This is another function")


cli()
