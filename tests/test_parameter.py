
from typing import Annotated
from taskcli.parameter import Parameter
from taskcli import arg
from taskcli.task import Task

def test_basic():

    def foo(x):
        pass

    task = Task(foo)
    param = task.params[0]
    assert param.name == "x"
    assert param.type == Parameter.Empty



def test_basic_types_from_signature():

    def foo(x:str):
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == Parameter.Empty
    assert not param.has_default()

def test_basic_types_from_annotated():
    def foo(x:Annotated[str, None]):
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == Parameter.Empty
    assert not param.has_default()


def test_basic_default_from_param():
    def foo(x:str="foobar"):
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == "foobar"
    assert param.has_default()


def test_basic_default_from_annotated():
    xxx = arg(str, default="from-annotated")
    def foo(x:xxx):
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == "from-annotated"
    assert param.has_default()


def test_basic_default_from_param_and_annotated():
    xxx = arg(str, default="from-annotated")
    def foo(x:xxx, y:xxx="from-signature", ):
        pass

    task = Task(foo)
    param1 = task.params[0]
    param2 = task.params[1]

    assert param1.name == "x"
    assert param1.type == str
    assert param1.default == "from-annotated"
    assert param1.has_default()

    assert param2.name == "y"
    assert param2.type == str
    assert param2.default == "from-signature"
    assert param2.has_default()

def test_basic_no_default_but_annotated():
    xxx = arg(str)
    def foo(x:xxx):
        pass

    param = Task(foo).params[0]
    assert param.name == "x"
    assert param.type == str
    assert param.default == Parameter.Empty
    assert not param.has_default()