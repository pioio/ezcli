import foobar
import taskcli

from taskcli import task, tt
import os




@task
def task_d2():
    cwd = os.getcwd()
    print("Hello from sometasks_task(), calling foobar.foo()", cwd)

    foobar.foo()

if __name__ == "__main__":
    tt.dispatch()
