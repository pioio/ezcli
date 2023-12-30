from taskcli import task, tt
import taskcli.include

from . import moduleb


with tt.Group("groupA", namespace="nsA"):
    taskcli.include.include(moduleb)

    @task
    def taska() -> str:
        return "a"

