#!/usr/bin/env python3

#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import os
import logging
import argparse


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


# =============================================================


def main():
    parser = argparse.ArgumentParser(description="uncrustify-impact")
    # parser.add_argument("--listtools", action="store_true", help="List tools")
    # parser.set_defaults(func=None)

    ## =================================================

    args = parser.parse_args()

    # logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    print("xxx:", args)

    _LOGGER.info("Completed")
    return 0


## ============================= main section ===================================


if __name__ == "__main__":
    EXIT_CODE = main()
    sys.exit(EXIT_CODE)
