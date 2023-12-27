#!/usr/bin/env python

from taskcli import task, run, tt



@task
def task1(arg1: str) -> None:
    assert isinstance(arg1, str)
    print(arg1)

@task
def task2(arg1: str, arg2: str) -> None:
    assert isinstance(arg1, str)
    assert isinstance(arg2, str)
    print(arg1, arg2)

@task
def task3(arg1: str,*, arg2: str) -> None:
    assert isinstance(arg1, str)
    assert isinstance(arg2, str)
    print(arg1, arg2)

@task
def task4(arg1: str,*, arg2: int) -> None:
    assert isinstance(arg1, str)
    assert isinstance(arg2, int)
    print(arg1, arg2)

@task
def task5(arg1: float,*, arg2: int) -> None:
    assert isinstance(arg1, float)
    assert isinstance(arg2, int)
    print(arg1, arg2)

#######################################################################################################################
# Lists
@task
def task_list1_a(*, arg1: list[float]=["foo"]) -> None: # positional list
    #print(arg1)
    assert isinstance(arg1, list), f"arg1 is not a list, but a {type(arg1)}"
    for item in arg1:
        assert isinstance(item, float), f"item is not a float, but a {type(item)}"

    print(arg1)


@task
def task_list1_b(arg1: list[float]) -> None: # optional list
    assert isinstance(arg1, list), f"arg1 is not a list, but a {type(arg1)}"
    for item in arg1:
        assert isinstance(item, float), f"item is not a float, but a {type(item)}"

    print(arg1)


########################################################################################################################
# bools
@task
def task_bool1(*, arg1: bool) -> None:
    assert isinstance(arg1, bool)
    print(arg1)


@task
def task_bool1_error(arg1xx: bool) -> None:
    """This one should result in error when attempting to run it, but no for task cli (only warning there)."""
    msg = "We should never even get here."
    print(msg)
    raise Exception(msg)

@task
def task_bool2(*, arg1: bool, arg2: int) -> None:
    assert isinstance(arg1, bool)
    assert isinstance(arg2, int)
    print(arg1, arg2)



@task
def task_complex1(arg1:int,  arg2:float=3.0, *, arg3: bool, arg4: int=44) -> None:
    assert isinstance(arg1, int)
    assert isinstance(arg2, float)
    assert isinstance(arg3, bool)
    assert isinstance(arg4, int)
    print(arg1, arg2, arg3, arg4)


# FIXME:
# This is causing issue in the unit test
# def task_complex1(arg1:int,  arg2:float=3.0, /, *, arg3: bool, arg4: int=44) -> None:

if __name__ == "__main__":
    tt.dispatch()
