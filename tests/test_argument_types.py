# XXXX TODO: what to do with mandatory lists?  if positional - mandatory one element, if keyword, optional?

import pytest


from . import tools
from taskcli import task, tt
from .tools import reset_context_before_each_test

result = []

def assert_is_list_of(obj, typevar):
    assert isinstance(obj, list)
    for item in obj:
        assert isinstance(item, typevar)


def test_1():
    @task
    def foo():
        pass

    tools.include_task().dispatch()
    assert result == []


def test_positional_lists_default_in_annotation_does_not_require_passing_anything():
    Paths = tt.arg(list[str], default=[".", "src"])

    @task
    def foo(paths:Paths):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"]
    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["1", "2"]) == ["1", "2"]


def test_positional_lists_with_default_in_signature_does_not_require_passing_anything():
    Paths = tt.arg(list[str])

    @task
    def foo(paths:Paths=[".", "src"]):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"]
    assert t.dispatch(["path"]) == ["path"]


def test_positional_list_with_no_defaults_requires_passing_at_least_one(capsys):
    """The list has no default values, so providing at least one element is mandatory"""
    Paths = tt.arg(list[str])

    @task
    def foo(paths:Paths):
        return paths

    t = tools.include_task()

    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["path", "path2"]) == ["path", "path2"]
    with pytest.raises(SystemExit, match="2"):
        t.dispatch()
    assert capsys.readouterr().err.endswith("error: the following arguments are required: paths\n")




def test_keyword_lists_default_in_annotation_does_not_require_passing_anything():
    Paths = tt.arg(list[str], default=[".", "src"])

    @task
    def foo(*, paths:Paths):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"]
    assert t.dispatch(["--paths", "path"]) == ["path"]
    assert t.dispatch(["--paths", "1", "2"]) == ["1", "2"]
    assert t.dispatch(["--paths", "1", "--paths", "2"]) == ["2"] # The first one will be ignores


def test_keyword_lists_default_in_annotation_does_not_require_passing_anything_integers():
    Paths = tt.arg(list[int], default=[1,2,3])

    @task
    def foo(*, paths:Paths, names:list[str]=["foobar"]):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [1,2,3]
    assert t.dispatch(["--paths", "1"]) == [1]
    assert t.dispatch(["--paths", "1", "2"]) == [1, 2]


def test_keyword_list_with_no_defaults_requires_passing_at_least_one_arg(capsys):
    """The list has no default value, so providing at least one element is mandatory"""
    Paths = tt.arg(list[int])

    @task
    def foo(*, paths:Paths):
        return paths

    t = tools.include_task()

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()
    assert capsys.readouterr().err.endswith("error: the following arguments are required: --paths\n")


def test_list_or_none(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths:list|None):
        return paths

    t = tools.include_task()

    assert t.dispatch(["foo"]) == ["foo"]
    assert t.dispatch(["path1", "path2", "path3", "path4"]) == ["path1", "path2", "path3", "path4"]

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()

    assert capsys.readouterr().err.endswith("error: the following arguments are required: paths\n")


def test_list_int_or_none(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths:list[int]|None):
        return paths

    t = tools.include_task()

    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["path1", "path2", "path3", "path4"]) == ["path1", "path2", "path3", "path4"]

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()

    assert capsys.readouterr().err.endswith("error: the following arguments are required: paths\n")


def test_list_simple(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths:list):
        return paths

    t = tools.include_task()

    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["path1", "path2", "path3", "1"]) == ["path1", "path2", "path3", "1"]

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()

    assert capsys.readouterr().err.endswith("error: the following arguments are required: paths\n")
