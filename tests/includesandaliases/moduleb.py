from taskcli import task, tt

from . import modulec


with tt.Group("groupB", namespace="nsB"):
    @task
    def taskb() -> str:
        return "a"

    tt.include(modulec)