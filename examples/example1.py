#!/usr/bin/env python


import logging


from taskcli import task, cli

log = logging.getLogger(__name__)
import common

common.setup_logging()


@task
def simple_function():
    log.info("This is a simple function")


@task
def another_function():
    log.info("This is another function")


simple_function()
cli()
