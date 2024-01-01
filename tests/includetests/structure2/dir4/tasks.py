#!/usr/bin/env python3

from taskcli import task, tt

# This file is unrelated to the other 3. Not used by them, not using them
# It's here to test that from within dir2/subdir1, we can safely run this tasks,
# while ignoring any tasks.py in between here and there
from foobar import foo

@task
def d4t1():
    print("Hello from d4t1")
    foo()


if __name__ == "__main__":
    tt.dispatch()
