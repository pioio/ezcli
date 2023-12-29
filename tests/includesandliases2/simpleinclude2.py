from taskcli import task, tt


@task(aliases="t0")
def task0() -> str:
    return "0"

with tt.Group("groupS", namespace="groupS", alias_namespace="gS"):
    @task(aliases="t1")
    def task1() -> str:
        return "1"


    @task()
    def task2() -> str:
        return "2"