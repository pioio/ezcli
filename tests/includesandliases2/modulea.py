
from taskcli import task, tt

from . import moduleb


with tt.Group("groupA", namespace="group_nsA"):
    tt.include(moduleb, namespace="include_nsA")

    @task
    def taska() -> str:
        return "a"

