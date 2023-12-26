import taskcli
from taskcli import task

def customize_parser(parser):
    """Customize the argparse parser."""
    parser.add_argument("--custom-arg", action="store_true", help="Custom argument")

@task(customize_parser)
def run():
    """Run the taskcli."""
    taskcli.run()
