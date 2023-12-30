from taskcli import constants, task, tt
from taskcli.listing import create_groups, list_tasks

from . import tools
from .tools import reset_context_before_each_test


def test_basic_nested_groups():
    with tt.Group("parent1"):

        @task
        def task_in_parent1():
            pass

        with tt.Group("child1"):

            @task
            def task_in_child1():
                pass

            @task(hidden=True)
            def task_in_child1_hidden():
                pass

    with tt.Group("parent2"):

        @task
        def foobar():
            pass

    with tools.simple_list_format():
        lines = list_tasks(tt.get_tasks())

    output = "\n".join(lines)
    assert (
        output
        == """# parent1
task-in-parent1
  # child1
  task-in-child1
  1 hidden

# parent2
foobar"""
    )


def test_parent_with_children_but_no_tasks_of_its_own():
    with tt.Group("parent1") as g1:
        with tt.Group("child1"):

            @task
            def task_in_child1():
                pass

        with tt.Group("child2"):

            @task
            def task_in_child2():
                pass

    with tt.Group("foobar") as g2:

        @task
        def task_in_foobar():
            pass

    tasks = tt.get_tasks()
    assert len(tasks) == 3

    top_groups = create_groups(tasks)
    assert top_groups == [g1, g2]

    with tools.simple_list_format():
        lines = list_tasks(tasks)

    output = "\n".join(lines)
    assert (
        output
        == """# parent1
  # child1
  task-in-child1
  # child2
  task-in-child2

# foobar
task-in-foobar"""
    )


def test_parent_with_all_hidden_children():
    with tt.Group("parent1") as g1:  # NOT hidden
        with tt.Group("child1", hidden=True):

            @task
            def task_in_child1():
                pass

        with tt.Group("child2", hidden=True):

            @task
            def task_in_child2():
                pass

    # we need at least one visible
    @task
    def task_in_child3():
        pass

    tasks = tt.get_tasks()
    assert len(tasks) == 3
    with tools.simple_list_format():
        lines = list_tasks(tasks)

    output = "\n".join(lines)
    assert (
        output
        == f"""# default
task-in-child3
Also 2 hidden groups, with 2 tasks in them, {constants.HELP_TEXT_USE_H_TO_SHOW_HIDDEN}"""
    )


def test_parent_with_all_hidden_children2():
    with tt.Group("parent1", hidden=True) as g1:

        @task(hidden=False)
        def sometask():
            pass

        with tt.Group("child1", hidden=True):

            @task
            def task_in_child1():
                pass

        with tt.Group("child2", hidden=True):

            @task
            def task_in_child2():
                pass

    # we need at least one visible
    @task
    def task_in_child3():
        pass

    tasks = tt.get_tasks()
    assert len(tasks) == 4
    with tools.simple_list_format():
        lines = list_tasks(tasks)

    expected = f"""# default
task-in-child3
Also 3 hidden groups, with 3 tasks in them, {constants.HELP_TEXT_USE_H_TO_SHOW_HIDDEN}""".split("\n")

    assert lines == expected


def test_parent_with_all_hidden_children3():
    with tt.Group("parent1", hidden=False) as g1:  # <<--- NOT hidden !!

        @task(hidden=True)
        def sometask():
            pass

        with tt.Group("child1", hidden=True):

            @task
            def task_in_child1():
                pass

        with tt.Group("child2", hidden=True):

            @task
            def task_in_child2():
                pass

    # we need at least one visible
    @task
    def task_in_child3():
        pass

    tasks = tt.get_tasks()
    assert len(tasks) == 4
    with tools.simple_list_format():
        lines = list_tasks(tasks)

    expected = f"""# parent1
1 hidden

# default
task-in-child3
Also 2 hidden groups, with 2 tasks in them, {constants.HELP_TEXT_USE_H_TO_SHOW_HIDDEN}""".split("\n")

    assert lines == expected


def test_visible_group_with_only_hidden_child_should_be_shown_and_list_num_hidden():
    """In this case, since group is not hidden, one would expect to see the group, with 'hidden 1' entry."""

    with tt.Group("parent1", hidden=False) as g1:  # <<--- NOT hidden !!

        @task(hidden=True)  # <<<--- hidden
        def sometask():
            pass

    # we need at least one visible
    @task
    def task_in_child2():
        pass

    tasks = tt.get_tasks()
    assert len(tasks) == 2
    with tools.simple_list_format():
        lines = list_tasks(tasks)

    expected = """# parent1
1 hidden

# default
task-in-child2""".split("\n")

    assert lines == expected
