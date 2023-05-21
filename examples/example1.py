#!/usr/bin/env python3

from taskcli import task, cli, arg
import logging

from taskcli.taskcli import mock_decorator

log = logging.getLogger(__name__)
logging = logging.basicConfig(level=logging.DEBUG)

# @task()
# def add_no_type(a,b):
#     # no type, defaults to str
#     assert isinstance(a, str)
#     assert isinstance(b, str)
#     log.info (a + b)   # this will concatanate the strings
#     return a + b


@task()
#@arg("a", type=str)
#@arg("b", type=str, help="bbb")
def add_typed_int(a:int,b:int):
    # no type, defaults to str
    assert isinstance(a, int)
    assert isinstance(b, int)
    log.info (a + b)


# @task()
# @mock_decorator()
# def add_typed_int_with_decorator(a:int,b:int):
#     # no type, defaults to str
#     assert isinstance(a, int)
#     assert isinstance(b, int)
#     #print(type(a))
#     log.info (a + b)
#     return a + b




# @task()
# def add_floats(a: float, b:float):
#     # no type, defaults to str
#     assert isinstance(a, float)
#     assert isinstance(b, float)
#     #print(type(a))
#     log.info (a + b)
#     return a + b


# @task
# def abool(a:bool):
#     assert isinstance(a, bool)
#     log.info(a)
#     return a

# @task
# def call_abool():
#     assert abool("False") == False
#     assert abool("0") == False
#     assert abool("foo") == True
#     assert abool("True") == True




cli()