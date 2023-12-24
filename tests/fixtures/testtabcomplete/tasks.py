#!/usr/bin/env python
import dis

from taskcli import dispatch, task


@task
def foobar():
    pass


if __name__ == "__main__":
    dispatch()
