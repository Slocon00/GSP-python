import logging
import sys

logging.basicConfig(level=logging.NOTSET, stream=sys.stdout,
                    format="%(levelname)s:%(module)s:%(message)s", force=True)
