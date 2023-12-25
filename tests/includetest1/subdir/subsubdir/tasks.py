import os

from taskcli import dispatch, include, task


@task
def subsubchild() -> None:
    pass
