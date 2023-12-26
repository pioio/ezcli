import argparse
import sys

import taskcli
from taskcli import Task, task

from .utils import include_tasks, reset_context_before_each_test

sideeffect = 0


def test_alphanumeric_order():
    """Test by default important tasks come first, all within alphanumeric order."""

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
    show_hidden_tasks = 3
    lines = taskcli.listing.list_tasks(tasks, verbose=show_hidden_tasks)
    lines = "\n".join(lines)
    assert lines == """* a-imporant1
* z-imporant2
* a-regular1
* b-hidden1
* c-regular2
* d-hidden2""", "important tasks should be first, the rest should come in alphanumeric order"
