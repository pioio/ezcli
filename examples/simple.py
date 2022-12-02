#!/usr/bin/env python3
from taskcli import task, cli


@task()
def t1():
    """ Do another thing """
    print("And this is t1 ")

@task()
def t2(z, x=False):
    """ Do this and that """
    print(f"Hello from t2, z={z}, x={x}!!")

@task()
def t3(arg1, arg2, arg3, x=False):
    """ Do this and that """
    print(f"Hello from t3!!")


if __name__ == "__main__":
    cli()