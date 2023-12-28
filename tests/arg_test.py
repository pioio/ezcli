from taskcli import arg, task, tt

from . import tools
from .tools import reset_context_before_each_test


def test_setting_nargs_works():
    Paths = tt.arg(str, "The paths to lint", nargs="*")

    @task
    def foobar(paths: Paths):
        return paths

    t = tools.include_task()
    assert t.dispatch(["x", "x"]) == ["x", "x"]
