from taskcli import Task
from taskcli.listing import ORDER_TYPE_ALPHA, _sort_tasks
from taskcli import Group

i1 = Task(lambda: None, group=Group("foo"), name="aimportant1",  important=True)
i2 = Task(lambda: None, group=Group("foo"), name="zimportant2", important=True)
n1 = Task(lambda: None, group=Group("foo"), name="anormal1")
n2 = Task(lambda: None, group=Group("foo"), name="znormal2")

h2 = Task(lambda: None, group=Group("foo"), name="zhidden2", hidden=True)
h1 = Task(lambda: None, group=Group("foo"), name="ahidden1", hidden=True)


def test_basic():
    res = _sort_tasks([h1, h2, n2, n1, i2, i1], sort_important_first=True, sort_hidden_last=True)
    assert res == [i1, i2, n1, n2, h1, h2]


def test_basic2():
    res = _sort_tasks([h1, h2, n2, n1, i2, i1], sort_important_first=True, sort_hidden_last=False)
    assert res == [i1, i2, h1, n1, h2, n2]


def test_basic3_simple():
    res = _sort_tasks([n1, i1, h1], sort_important_first=False, sort_hidden_last=False)
    assert res == [h1, i1, n1]


def test_basic3():
    res = _sort_tasks([h1, h2, n2, n1, i2, i1], sort_important_first=False, sort_hidden_last=False)
    assert res == [h1, i1, n1, h2, i2, n2]


def test_basic4():
    res = _sort_tasks([h1, h2, n2, n1, i2, i1], sort_important_first=False, sort_hidden_last=True)
    assert res == [i1, n1, i2, n2, h1, h2]
