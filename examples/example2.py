#!/usr/bin/env python3

from taskcli import task, arg, cli
import logging

log = logging.getLogger(__name__)
logging = logging.basicConfig(level=logging.DEBUG)


@task
@arg("a", nargs="+", type=int)  # FIXME, without @arg here this results a list of strings
def list_ints_with_arg_but_no_type(a):
    assert isinstance(a, list)
    assert isinstance(a[0], int), f"Expected int inside the list, got {type(a[0])}"
    log.info(a)
    return a


@task
@arg("a", nargs="+", type=int)
def list_ints_with_arg(a):
    assert isinstance(a, list)
    assert isinstance(a[0], int), f"Expected int, got {type(a[0])}"
    log.info(a)
    return a


# @task
# def list_ints_no_arg(a:list[int]):
#     assert isinstance(a, list)
#     assert isinstance(a[0], str)
#     log.info(a)
#     return a

cli()
