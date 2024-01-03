import re
from json import tool


import taskcli
from taskcli import Group, Task, arg, constants, listing, task, tt
from taskcli.dispatching import dispatch
from taskcli.listing import list_tasks
from taskcli.taskcliconfig import TaskCLIConfig
from taskcli.taskrendersettings import TaskRenderSettings, new_settings

from . import tools
from .test_including import clean_stdout
from .tools import include_tasks, reset_context_before_each_test

sideeffect = 0


def test_listing_tasks_works():
    @task
    def foobar1():
        """This is the first task"""

    tasks = tools.include_tasks()
    with tools.simple_list_format():
        lines = list_tasks(tasks)
    assert len(lines) == 2
    assert re.match(r"foobar1\s+This is the first task", lines[1])


def test_alphanumeric_order():
    """Test that by default important tasks come first, all within alphanumeric order."""

    @task(hidden=True)
    def d_hidden2():
        pass

    @task()
    def c_regular2():
        pass

    @task()
    def a_regular1():
        pass

    @task(important=True)
    def z_imporant2():
        pass

    @task(hidden=True)
    def b_hidden1():
        pass

    @task(important=True)
    def a_imporant1():
        pass



    tasks = include_tasks()

    # force sorting important tasks first
    tasks[0].group.sort_important_first = True
    tasks[0].group.sort_hidden_last = True

    show_hidden_tasks = 3
    settings = TaskRenderSettings()
    settings.show_hidden_tasks = True
    with tools.simple_list_format():
        lines = taskcli.listing.list_tasks(tasks, settings=settings)
    linestxt = "\n".join(lines)
    assert (
        linestxt
        == """# default
a-imporant1
z-imporant2
a-regular1
c-regular2
b-hidden1
d-hidden2"""
    ), "important tasks should be first, the rest should come in alphanumeric order"


def test_list_everything_works(capsys):
    """Test that using -L results in listing everything we can list."""

    hidden_group = Group("hidden-group", hidden=True)

    @task()
    def not_hidden_task():
        pass

    @task(hidden=True)
    def hidden_task():
        pass

    @task(group=hidden_group)
    def task_in_hidden_group():
        pass

    include_tasks()

    with tools.simple_list_format():
        dispatch(["-L"])

    stdout = capsys.readouterr().out
    clean_stdout(stdout)
    assert (
        stdout
        == """# default
hidden-task
not-hidden-task

# hidden-group HIDDEN
task-in-hidden-group
"""
    )


def test_positional_mandatory_args_are_listed_by_default():
    @task
    def foobar(name: int) -> None:
        """This is the first task"""

    tasks = tools.include_tasks()

    with tools.simple_list_format():
        lines = list_tasks(tasks)
    assert len(lines) == 2
    assert re.match(r"foobar\s+NAME\s+.*$", lines[1])


def test_positional_optional_args_are_not_listed_by_default():
    @task
    def foobar(paths: list[str] = ["src/"]) -> None:  # noqa:  B006
        """This is the first task"""

    tasks = tools.include_tasks()

    with tools.simple_list_format():
        lines = list_tasks(tasks)
    assert len(lines) == 2

    assert re.match(
        r"foobar\s+This is the first task", lines[1]
    ), "Since we have a default, we should not see it listed"


def test_list_short_args_share_line_with_summary_no_default():
    @task
    def foobar(paths: list[str]) -> None:
        """This is the first task"""

    tasks = tools.include_tasks()

    with tools.simple_list_format():
        lines = list_tasks(tasks)
    assert len(lines) == 2

    assert re.match(r"foobar\s+PATHS\s+This is the first task", lines[1]), "No default, so it should appear"


def test_list_important_optional_args_are_always_shown():
    Name = arg(str, important=True)
    Text = arg(str)

    @task
    def foobar(message: Text = "some text", name: Name = "alice") -> None:  # type: ignore # noqa: PGH003
        """This is the first task"""

    tasks = tools.include_tasks()

    with tools.simple_list_format():
        lines = list_tasks(tasks)
    assert len(lines) == 2
    assert re.match(
        r"foobar\s+NAME\s+This is the first task", lines[1]
    ), "Text is optional, but not important, so it should not be shown. Name is optional, but important, so show it."


def test_hidden_tasks_dont_show_up_by_default():
    @task
    def foobar(paths: list[str]) -> None:
        """This is the first task"""

    @task(hidden=True)
    def hidden_task() -> None:
        """This is the hidden task"""

    tasks = tools.include_tasks()

    with tools.simple_list_format():
        lines = list_tasks(tasks)

    task_names = [task.name for task in tasks]
    assert "hidden-task" in task_names, "Hidden task should be in the list of tasks, but it is not"

    for line in lines:
        assert (
            "hidden-task" not in line
        ), f"Hidden task should be missing from listing by default, but it is not, line: {line}"

    from taskcli.taskrendersettings import TaskRenderSettings

    render_settings = TaskRenderSettings()
    render_settings.show_hidden_tasks = True
    lines = list_tasks(tasks, settings=render_settings)
    assert "hidden-task" in "\n".join(lines), "Hidden task should be in the task listing when high verbose"


def test_list_with_tags():
    groupa = Group("groupA")
    groupb = Group("groupB")

    @task(tags=["tag1", "groupa"], group=groupa)
    def foobar() -> None:
        pass

    @task(tags=["tag2", "tag2a"], group=groupb)
    def foobar2a() -> None:
        pass

    @task(tags=["tag2"], hidden=True, group=groupb)
    def foobar2b() -> None:
        pass

    tasks = tools.include_tasks()

    with tools.simple_list_format():
        lines = list_tasks(tasks)
    assert (
        lines
        == """# groupA
foobar

# groupB
foobar2a
1 hidden
""".strip().splitlines()
    )

    with tools.simple_list_format():
        config = TaskCLIConfig()
        config.tags = ["tag1", "tag2"]
        config.show_tags = False
        render_settings = new_settings(config=config)  # to translate config into render settings
        with tools.simple_list_format():
            lines = list_tasks(tasks, settings=render_settings)
    assert (
        lines
        == """# groupA
foobar

# groupB
foobar2a
foobar2b
""".strip().splitlines()
    )

    with tools.simple_list_format():
        config = TaskCLIConfig()
        config.tags = ["tag2"]
        config.show_tags = False
        render_settings = new_settings(config=config)  # to translate config into render settings
        with tools.simple_list_format():
            lines = list_tasks(tasks, render_settings)
    assert (
        lines
        == """# groupB
foobar2a
foobar2b""".split(
            "\n"
        )
    )

    with tools.simple_list_format():
        config = TaskCLIConfig()
        config.tags = ["tag1"]
        config.show_tags = False
        render_settings = new_settings(config=config)  # to translate config into render settings
        with tools.simple_list_format():
            lines = list_tasks(tasks, render_settings)
    assert (
        lines
        == """# groupA
foobar""".split(
            "\n"
        )
    )


def test_default_group_always_first():
    with tt.Group("GroupA"):

        @task
        def task_in_group_a() -> None:
            pass

    @task
    def task_in_default_group() -> None:
        pass

    with tools.simple_list_format():
        config = TaskCLIConfig()
        settings = new_settings(config=TaskCLIConfig())
        lines = list_tasks(tools.include_tasks(), settings=settings)
        assert lines[0] == "# default"

def test_hidden_tasks_show_up_during_search():
    @task
    def foobar(*, hidden=True) -> None:
        pass

    with tools.simple_list_format():
        config = TaskCLIConfig()
        config.search = "oo"
        settings = new_settings(config=TaskCLIConfig())
        with tools.simple_list_format():
            lines = list_tasks(tools.include_tasks())
        assert lines[0] == "# default"
        assert lines[1] == "foobar"
