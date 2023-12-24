#!/usr/bin/env python
import taskcli
from taskcli import task, Arg

from typing import Annotated
@task
def task1(*,force1:bool=False) -> None:
    print("task1")

@task
def task2(realm:int=1, *, force2:bool=False) -> None:
    print("task2")


Force3 = Annotated[bool, "Help text"]

@task
def task3(realm:int=1, *, force3:Force3=False) -> None:
    print("task2")

if __name__ == "__main__":
    taskcli.dispatch()
