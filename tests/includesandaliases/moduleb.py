import taskcli.include
from taskcli import task, tt

from . import modulec

with tt.Group("groupB", name_namespace="nsB"):

    @task
    def taskb() -> str:
        return "a"

    taskcli.include.include(modulec)
