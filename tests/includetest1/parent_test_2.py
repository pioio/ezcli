#!/usr/bin/env python3
import dis
from taskcli import task, include, dispatch

import subdir.subsubdir.tasks as child_tasks2
import os

include(child_tasks2)


if __name__ == "__main__":
    child_tasks2.subsubchild()
    dispatch()
