#!/usr/bin/env python

import taskcli as tc

# This is the most basic example.
# setting up logging is optional.
import logging

log = logging.getLogger(__name__)
import common

common.setup_logging()


@tc.task()
def foobar(arg1: int, arg2: bool, arg3: str, arg4: list[int]):
    """An example task
    arg1: this is an integer argument
    arg2: this is a boolean argument
    arg3: this is a string argument
    arg4: list of integers
    """
    print("arg1: ", arg1)
    print("arg2: ", arg2)
    print("arg3: ", arg3)
    print("arg4: ", arg4)


tc.cli()
