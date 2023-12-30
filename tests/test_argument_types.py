import pytest

from taskcli import task, tt
from taskcli.task import UserError

from . import tools
from .tools import reset_context_before_each_test

result = []


########################################################################################################################
# Helpers
def assert_unsupported_type_warning_was_printed(capsys):
    error = "Warning: Task 'foo' has a parameter 'paths' which has an unsupported"
    err = capsys.readouterr().err
    assert error in err

    hint = "Add `suppress_warnings=True`"
    assert hint in err


def assert_param_required_printed(capsys, name):
    assert capsys.readouterr().err.endswith(f"error: the following arguments are required: {name}\n")


def assert_is_list_of(obj, typevar):
    assert isinstance(obj, list)
    for item in obj:
        assert isinstance(item, typevar)


########################################################################################################################
# tests


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
    def foo(paths: Paths):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"]  # default value should be used
    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["1", "2"]) == ["1", "2"]


def test_positional_lists_with_default_in_signature_does_not_require_passing_anything():
    Paths = tt.arg(list[str])

    @task
    def foo(paths: Paths = [".", "src"]):  # noqa: B006
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"]  # default value should be used
    assert t.dispatch(["path"]) == ["path"]


def test_positional_list_with_no_defaults_requires_passing_at_least_one_arg(capsys):
    """The list has no default values, so providing at least one element is mandatory"""
    Paths = tt.arg(list[str])

    @task
    def foo(paths: Paths):
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
    def foo(*, paths: Paths):
        return paths

    t = tools.include_task()
    assert t.dispatch() == [".", "src"]
    assert t.dispatch(["--paths", "path"]) == ["path"]
    assert t.dispatch(["--paths", "1", "2"]) == ["1", "2"]
    assert t.dispatch(["--paths", "1", "--paths", "2"]) == ["2"]  # The first one will be ignores


def test_keyword_lists_default_in_annotation_does_not_require_passing_anything_integers():
    Sizes = tt.arg(list[int], default=[1, 2, 3])

    @task
    def foo(*, sizes: Sizes, names: list[str] = ["foobar"]):  # noqa: B006
        return sizes

    t = tools.include_task()
    assert t.dispatch() == [1, 2, 3]
    assert t.dispatch(["--sizes", "1"]) == [1]
    assert t.dispatch(["--sizes", "1", "2"]) == [1, 2]

    from taskcli.task import UserError

    with pytest.raises(UserError, match="Could not convert 'foobar' to <class 'int'>"):
        t.dispatch(["--sizes", "foobar"], sysexit_on_user_error=False)


def test_keyword_list_with_no_defaults_requires_passing_at_least_one_arg(capsys):
    """The list has no default value, so providing at least one element is mandatory"""
    Paths = tt.arg(list[int])

    @task
    def foo(*, paths: Paths):
        return paths

    t = tools.include_task()

    assert t.dispatch(["--paths", "1", "2", "3"]) == [1, 2, 3]

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()
    assert capsys.readouterr().err.endswith("error: the following arguments are required: --paths/-p\n")


##########################################################################################
# or none


def test_list_or_none(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths: list | None):
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
    def foo(paths: list[int] | None):
        return paths

    t = tools.include_task()

    assert t.dispatch(["1", "2"]) == [1, 2]
    with pytest.raises(UserError, match="Could not convert 'path' to <class 'int'>"):
        assert t.dispatch(["path"], sysexit_on_user_error=False) == ["path"]
    with pytest.raises(UserError, match="Could not convert 'path1' to <class 'int'>"):
        assert t.dispatch(["path1", "path2", "path3", "path4"], sysexit_on_user_error=False) == [
            "path1",
            "path2",
            "path3",
            "path4",
        ]

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()

    assert capsys.readouterr().err.endswith("error: the following arguments are required: paths\n")


def test_list_int_or_none_default_none():
    """The list has a default value, so providing at least one element is not mandatory."""

    @task
    def foo(paths: list[int] | None = None):
        return paths

    t = tools.include_task()

    assert t.dispatch() is None
    assert t.dispatch(["1", "2"]) == [1, 2]

    with pytest.raises(UserError, match="Could not convert 'path' to <class 'int'>"):
        assert t.dispatch(["path"], sysexit_on_user_error=False) == ["path"]

    with pytest.raises(UserError, match="Could not convert 'path1' to <class 'int'>"):
        assert t.dispatch(["path1", "path2", "path3", "path4"], sysexit_on_user_error=False) == [
            "path1",
            "path2",
            "path3",
            "path4",
        ]


def test_list_int_or_none_default_none_kw_arg():
    """The list has a default value, so providing at least one element is not mandatory."""

    @task
    def foo(*, paths: list[int] | None = None):
        return paths

    t = tools.include_task()

    assert t.dispatch() is None
    with pytest.raises(UserError, match="Could not convert 'path' to <class 'int'>"):
        assert t.dispatch(["--paths", "path"], sysexit_on_user_error=False) == ["path"]


def test_list_simple(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths: list):
        return paths

    t = tools.include_task()

    assert t.dispatch(["path"]) == ["path"]
    assert t.dispatch(["path1", "path2", "path3", "1"]) == ["path1", "path2", "path3", "1"]

    with pytest.raises(SystemExit, match="2"):
        t.dispatch()

    assert_param_required_printed(capsys, "paths")


def test_unsupported_param_types_with_no_defaults_cause_error(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths: dict):
        return paths

    t = tools.include_task()

    with pytest.raises(SystemExit, match="1"):
        t.dispatch()

    error = "The parameter does not have a default value set, so taskcli cannot skip adding it to argparse."
    assert error in capsys.readouterr().err


def test_unsupported_param_types_with_defaults_work_but_emit_warning(capsys):
    """The list has no default value, so providing at least one element is mandatory"""

    @task
    def foo(paths: dict = {}):  # noqa: B006
        return paths

    t = tools.include_task()

    assert t.dispatch() == {}
    assert_unsupported_type_warning_was_printed(capsys)


def test_unsupported_list_type_bool(capsys):
    @task
    def foo(paths: list[bool] = [True]):  # noqa: B006
        return paths

    t = tools.include_task()

    assert t.dispatch() == [True]
    assert_unsupported_type_warning_was_printed(capsys)


def test_tuples_result_in_unsupported_type(capsys):
    # TODO: we can be made to work with basic types, e.g. tuple[int,str,float]
    @task
    def foo(paths: tuple = (1,)):
        return paths

    t = tools.include_task()

    assert t.dispatch() == (1,)
    assert_unsupported_type_warning_was_printed(capsys)


def test_bool_positional_results_in_error(capsys):
    @task
    def foo(force=True):
        return force

    t = tools.include_task()

    with pytest.raises(SystemExit, match="1"):
        t.dispatch()

    error = "has a boolean parameter 'force' which is not keyword-only."
    assert error in capsys.readouterr().err


def test_bool_flag_with_no_default_is_required(capsys):
    @task
    def foo(*, force: bool):
        return force

    t = tools.include_task()
    with pytest.raises(SystemExit, match="2"):
        t.dispatch()

    assert_param_required_printed(capsys, "--force/--no-force/-f")


def test_bool_flag_works():
    @task
    def foo(*, force: bool = False):
        return force

    t = tools.include_task()
    assert t.dispatch("--force")
    assert not t.dispatch("--no-force")


def test_bools_without_type():
    @task
    def foo(*, force=False):
        return force

    t = tools.include_task()
    assert t.dispatch("--force")
    assert not t.dispatch("--no-force")


def test_complex_argument_example():
    Paths = tt.arg(list[str], default=[".", "src"])
    Sizes = tt.arg(list[int])

    @task
    def foo(paths: Paths, *, kwpaths: Paths, kwsizes: Sizes = [1, 2], force: bool = False):  # noqa: B006
        return paths, kwpaths, kwsizes, force

    t = tools.include_task()
    paths, kwpaths, kwsizes, force = t.dispatch(["--kwpaths", "foobar"])

    assert paths == [".", "src"]
    assert kwpaths == ["foobar"]
    assert kwsizes == [1, 2]
    assert force is False


def test_positional_arguments_with_hyphens():
    @task
    def foo(foo_bar: str):
        return foo_bar

    t = tools.include_task()
    assert t.dispatch("hello") == "hello"


def test_keyword_arguments_with_hyphens():
    @task
    def foo(*, foo_bar: str):
        return foo_bar

    t = tools.include_task()
    assert t.dispatch(["--foo-bar", "hello"]) == "hello"


def test_task_names_with_hyphens():
    @task
    def foo_bar(*, foo_bar: str):
        return foo_bar

    tools.include_task()
    from taskcli import dispatch

    assert dispatch(["foo-bar", "--foo-bar", "hello"]) == "hello"


def test_choices_str(capsys):
    Foobar = tt.arg(str, choices=["aaa", "bbb"])

    @task
    def foo_bar(foo_bar: Foobar):
        return foo_bar

    t = tools.include_task()
    assert t.dispatch("aaa") == "aaa"
    assert t.dispatch("bbb") == "bbb"
    with pytest.raises(SystemExit, match="2"):
        t.dispatch("ccc")
    assert capsys.readouterr().err.endswith(
        "error: argument foo_bar: invalid choice: 'ccc' (choose from 'aaa', 'bbb')\n"
    )


def test_choices_int(capsys):
    Foobar = tt.arg(int, choices=[111, 222])

    @task
    def foo_bar(foo_bar: Foobar):
        return foo_bar

    t = tools.include_task()
    assert t.dispatch("111") == 111
    assert t.dispatch("222") == 222
    with pytest.raises(SystemExit, match="2"):
        t.dispatch("333")


def test_support_for_vargs(capsys):
    @task
    def foo_bar(*args):
        return args

    t = tools.include_task()
    assert t.dispatch(["1", "2", "foo"]) == ("1", "2", "foo")


def test_support_for_vargs_with_type_are_strings():
    """TODO: convert them  ref:LIMITATION"""

    @task
    def foo_bar(*args: list[int]):
        return args

    t = tools.include_task()
    assert t.dispatch(["1", "2", "3"]) == ("1", "2", "3")


def test_support_for_vargs_with_arg():
    """In this case foobar gets parsed as kw-only arg, because *args eats up all positional args."""

    @task
    def foo_bar(*args, foobar: int):
        return args, foobar

    t = tools.include_task()
    import inspect

    assert t.params[1].kind == inspect.Parameter.KEYWORD_ONLY

    t.dispatch(["1", "2", "111", "--foobar", "22"], sysexit_on_user_error=False)


def test_support_for_vargs_with_arg_with_kwargs():
    """In this case foobar gets parsed as kw-only arg, because *args eats up all positional args."""

    @task
    def foo_bar(*args, foobar: int = 22, **kwargs):
        return args, foobar, kwargs

    t = tools.include_task()
    import inspect

    assert t.params[0].kind == inspect.Parameter.VAR_POSITIONAL
    assert t.params[1].kind == inspect.Parameter.KEYWORD_ONLY
    assert t.params[2].kind == inspect.Parameter.VAR_KEYWORD

    t.dispatch(["1", "2", "111"], sysexit_on_user_error=False)


def test_support_for_kwargs_basic():
    """Kwargs should be ignored by the parser"""

    @task
    def foo_bar(**kwargs):
        return kwargs

    t = tools.include_task()
    assert t.dispatch() == {}


def test_support_for_kwargs_and_args():
    """Kwargs should be ignored by the parser"""

    @task
    def foo_bar(*, force: bool = True, **kwargs):
        return force, kwargs

    t = tools.include_task()
    assert t.dispatch() == (True, {})

    assert t.dispatch("--no-force") == (False, {})


def test_support_for_vargs_and_kwargs():
    """args should be added to parses, kwargs should be ignored."""

    @task
    def foo_bar(*args, **kwargs):
        return args, kwargs

    t = tools.include_task()
    assert t.dispatch(["1", "2", "3"]) == (("1", "2", "3"), {})
