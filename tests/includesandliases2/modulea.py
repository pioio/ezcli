import taskcli.include
from taskcli import task, tt

from . import moduleb

with tt.Group("groupA", namespace="group_nsA"):
    taskcli.include.include(moduleb, name_namespace="include_nsA")

    @task
    def taska() -> str:
        return "a"
