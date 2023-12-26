#!/usr/bin/env python3
import taskcli
from taskcli import task

def customize_parser(parser):
    """Customize the argparse parser."""
    parser.add_argument("--custom-arg",
                        help="Custom argument", default=42)


@task(customize_parser=customize_parser)
def foobar():
    """Task which customizes the parser."""
    parsed_args = taskcli.get_runtime().parsed_args
    assert parsed_args is not None
    print("Value of custom-arg (set with --custom-arg <value>):", parsed_args.custom_arg)


if __name__ == "__main__":
    taskcli.dispatch()