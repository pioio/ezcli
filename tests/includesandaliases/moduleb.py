from taskcli import task, tt
import taskcli.include

from . import modulec


with tt.Group("groupB", namespace="nsB"):
    @task
    def taskb() -> str:
        return "a"

    taskcli.include.include(modulec)