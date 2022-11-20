# Common code for all examples
import sys
import logging


def setup_logging():

    level = logging.INFO
    if "-v" in sys.argv[1:]:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)7s: %(message)-50s     [%(filename)s:%(lineno)d]",
    )
