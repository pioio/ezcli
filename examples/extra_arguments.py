"""How to pass arbitrary arguments to tasks.

Tags: basic

Run:
- t -f FILENAME hash-it -- -sha256                                   # only extra args
- t -f FILENAME hash-it "Hello, Alice!"                                   # only positional arg
- t -f FILENAME hash-it "Hello, Bob!" -- -sha256 -hmac "secret"         # positional and extra args,
- t -f FILENAME hash-it "Hello, Charlie!" -r 3 -- -sha256 -hmac "secret"    # positional, options, and extra args

"""
import re
from taskcli import task, tt, run


@task
def hash_it(text="Hello, Foobar!", *, repeat:int=1):
    """Run a ping command and pass all extra args to it."""
    # Get the arguments as a list
    for arg in tt.get_extra_args_list():
        print("Extra arg: " + arg, flush=True)

    # Or, get them as a string, ready to be passed to a command
    # string will be empty if none were passed
    extra_args = tt.get_extra_args() or "-md5"

    for _ in range(repeat):
        run(f'echo -n "{text}" | openssl dgst {extra_args}')

