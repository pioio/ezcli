#!/usr/bin/env python
import taskcli
from taskcli import task, Arg

from typing import Annotated

@task
def foobar(name:str="xxx"):
    print(name)
    pass
