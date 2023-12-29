from taskcli import task, tt

@task
def taskb1() -> str:
    return "a"

with tt.Group("groupB", namespace="group_nsB"):
    @task(aliases="tb2")
    def taskb2() -> str:
        return "a"

