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


def test_simple_task_is_called():
    @task
    def foo():
        return "ok"

    assert tools.include_task().dispatch() == "ok"


def test_simple_task_raises_when_extra_args_specified():
    @task
    def foo():
        pass

    t = tools.include_task()
    with pytest.raises(SystemExit, match="2"):
        t.dispatch("some-arg")


def test_positional_lists_default_in_annotation_does_not_require_passing_anything():
    Paths = tt.arg(list[str], default=[".", "src"])

    @task
    def foo(paths:Paths):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"] # default value should be used
    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["1", "2"]) == ["1", "2"]


def test_positional_lists_with_default_in_signature_does_not_require_passing_anything():
    Paths = tt.arg(list[str])

    @task
    def foo(paths:Paths=[".", "src"]):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"]  # default value should be used
    assert t.dispatch(["path"]) == ["path"]


def test_positional_list_with_no_defaults_requires_passing_at_least_one_arg(capsys):
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


##########################################################################################
# or none

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
    """The list has no default value, so providing at least one element is mandatory."""

    @task
    def foo(paths:list[int]|None):
        return paths

    t = tools.include_task()

    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["path1", "path2", "path3", "path4"]) == ["path1", "path2", "path3", "path4"]

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()

    assert capsys.readouterr().err.endswith("error: the following arguments are required: paths\n")

def test_list_int_or_none_default_none():
    """The list has a default value, so providing at least one element is not mandatory."""

    @task
    def foo(paths:list[int]|None=None):
        return paths

    t = tools.include_task()

    assert t.dispatch() is None
    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["path1", "path2", "path3", "path4"]) == ["path1", "path2", "path3", "path4"]

def test_list_int_or_none_default_none_kw_arg():
    """The list has a default value, so providing at least one element is not mandatory."""

    @task
    def foo(*, paths:list[int]|None=None):
        return paths

    t = tools.include_task()

    assert t.dispatch() is None
    assert t.dispatch(["--paths", "path"]) == ["path"]


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



def test_unsupported_param_types_with_no_defaults_cause_error(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths:dict):
        return paths

    t = tools.include_task()

    with pytest.raises(SystemExit, match="1"):
        t.dispatch()

    error = "The parameter does not have a default value set, so taskcli cannot skip adding it to argparse."
    assert error in  capsys.readouterr().err


def test_unsupported_param_types_with_defaults_work_but_emit_warning(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths:dict={}):
        return paths

    t = tools.include_task()


    assert t.dispatch() == {}

    error = "Warning: Task 'foo' has a parameter 'paths' which has an unsupported"
    err =  capsys.readouterr().err
    assert error in  err

    hint = "Add `suppress_warnings=True`"
    assert hint in err



def test_complex_argument_example():
    Paths = tt.arg(list[str], default=[".", "src"])
    Sizes = tt.arg(list[int])
    @task
    def foo(paths:Paths, *, kwpaths:Paths, kwsizes:Sizes=[1,2], force:bool=False):
        return paths, kwpaths, kwsizes, force

    t = tools.include_task()
    paths, kwpaths, kwsizes, force = t.dispatch([ "--kwpaths", "foobar"])

    assert paths == [".", "src"]
    assert kwpaths == ["foobar"]
    assert kwsizes == [1,2]
    assert force == False
