
from taskcli import task, tt
import taskcli.include

from . import moduleb


with tt.Group("groupA", namespace="group_nsA"):
    taskcli.include.include(moduleb, namespace="include_nsA")

    @task
    def taska() -> str:
        return "a"

