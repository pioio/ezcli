from taskcli import task, tt


@task(aliases="t1")
def task1() -> str:
    return "1"


@task()
def task2() -> str:
    return "2"
