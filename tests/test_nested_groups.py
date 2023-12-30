from taskcli import task, tt
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
    assert output == """# parent1
task-in-parent1
  # child1
  task-in-child1
  1 hidden

# parent2
foobar"""



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
    assert output == """# parent1
  # child1
  task-in-child1
  # child2
  task-in-child2

# foobar
task-in-foobar"""
