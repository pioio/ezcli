import taskcli.include
from taskcli import task, tt

from . import moduleb

with tt.Group("groupA", name_namespace="nsA"):
    taskcli.include.include(moduleb)

    @task
    def taska() -> str:
        return "a"
