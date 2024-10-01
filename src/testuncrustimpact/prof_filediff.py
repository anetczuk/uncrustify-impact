#!/usr/bin/env python3
#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass


import os
import logging

import cProfile

import difflib


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# src_dir = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
# sys.path.insert(0, src_dir)


_LOGGER = logging.getLogger(__name__)


def read_lines(file_path):
    with open(file_path, encoding="utf-8") as item_file:
        return item_file.readlines()


# ===============================================


def run_profile():
    file_1 = "data/example_changed.cpp"
    file_1 = os.path.join(SCRIPT_DIR, file_1)
    file_2 = "data/example_changed2.cpp"
    file_2 = os.path.join(SCRIPT_DIR, file_2)

    lines_1 = read_lines(file_1)
    lines_2 = read_lines(file_2)

    ##
    result = difflib.ndiff(lines_1, lines_2)
    print("========= difflib.ndiff =========")
    print("".join(list(result)))

    ##
    result = difflib.context_diff(
        lines_1,
        lines_2,
        # fromfile='from.cpp', tofile='to.cpp',
        n=0,
        lineterm="",
    )
    print("========= difflib.context_diff =========")
    print(list(result))
    # print( "".join(list(result)) )

    ##
    result = difflib.unified_diff(
        lines_1,
        lines_2,
        # fromfile='from.cpp', tofile='to.cpp',
        n=0,
        lineterm="",
    )
    print("========= difflib.unified_diff =========")
    print(list(result))
    # print( "".join(list(result)) )


def main():
    prof_out_file = "/tmp/prof"
    cProfile.run("run_profile()", "/tmp/prof")

    print("to open results in interactive window run:")
    print(f"pyprof2calltree -k -i {prof_out_file}")


## ============================= main section ===================================


if __name__ == "__main__":
    main()
