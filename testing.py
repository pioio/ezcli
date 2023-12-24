#!/usr/bin/env python
from operator import is_
from typing import Annotated
from webbrowser import get
import taskcli
from taskcli import task
import inspect

import dataclasses

@dataclasses.dataclass
class Help:
    """Help"""
    x: str

Realm = Annotated[str, "help text"]


@task
def foo(realm: Realm) -> None:
    print(realm + "x")
    foo2(realm)

@task
def foo2(xxx: Annotated[str, "help text2"]) -> None:
    print("is instance:", isinstance(xxx, str))
    print(xxx + "x")

@task
def foo3(xxx) -> None:
    print(xxx + "x")

@task
def foo4(xxx:Realm) -> None:
    print(xxx + "x")

@task
def foo5(xxx: Annotated[int, "some help text"]) -> None:
    print(xxx + 4)

for fun in [foo, foo2, foo3, foo4, foo5]:
    print("------------ " + fun.__name__ + " ------------")
    signature = inspect.signature(fun)
    for param in signature.parameters.values():
        #print(param)
        #print(param.annotation)
        param_has_annotation = param.annotation is not inspect.Parameter.empty
        if param_has_annotation and getattr(param.annotation, "__metadata__", None) is not None:
            for metadata in param.annotation.__metadata__:
                print(metadata)

# foo("hello")