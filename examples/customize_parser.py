"""Shows how to customize the underlying `argparse` parser.

Tags: basic

Run:
- t -f FILENAME                 # list tasks
- t -f FILENAME foobar --help          # show help output
- t -f FILENAME foobar  --custom-arg 123   # use the custom argument we added

"""

import taskcli
from taskcli import task
import taskcli.core

def customize_parser(parser):
    """Customize the argparse parser."""
    parser.add_argument("--custom-arg",
                        help="Custom argument",
                        default=42,
                        type=int)


@task(customize_parser=customize_parser)
def foobar():
    """Task which customizes the parser."""
    parsed_args = taskcli.core.get_runtime().parsed_args
    assert parsed_args is not None
    print("Value of custom-arg (set with --custom-arg <value>):", parsed_args.custom_arg)
