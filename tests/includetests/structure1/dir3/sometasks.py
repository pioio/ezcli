
import taskcli

from taskcli import task, tt

import os
@task
def task_d3():
    import foobar # dir3 only imports during execution
    cwd = os.getcwd()
    print("Hello from sometasks_task() [dir3],  calling foobar.foo()", cwd)
    foobar.foo()


if __name__ == "__main__":
    tt.dispatch()
