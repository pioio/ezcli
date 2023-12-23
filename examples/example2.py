#!/usr/bin/env python3

import logging

from taskcli import arg, run, task

log = logging.getLogger(__name__)
logging = logging.basicConfig(level=logging.DEBUG)


@task
@arg(
    "a", nargs="+", type=int
)  # FIXME: without 'type' arg here, it results in a list of strings. We should be inferring type from the param type hint
def list_ints_with_arg_but_no_type(a: list[int]):
    assert isinstance(a, list)
    assert isinstance(a[0], int), f"Expected int inside the list, got {type(a[0])}"
    log.info(a)
    return a


@task
@arg("a", nargs="+", type=int)
def list_ints_with_arg(a: list[int]):
    assert isinstance(a, list)
    assert isinstance(a[0], int), f"Expected int, got {type(a[0])}"
    log.info(a)
    return a


if __name__ == "__main__":
    run()
