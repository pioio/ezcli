from taskcli import task, tt

from . import moduleb


with tt.Group("groupA", namespace="nsA"):
    tt.include(moduleb)

    @task
    def taska() -> str:
        return "a"

