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
from glob import glob

from uncrustimpact.cfgparser import print_params_space
from uncrustimpact.impact import calculate_impact


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


# =============================================================


def gen_params_space_dict_tool(_args):
    print_params_space()
    _LOGGER.info("Completed")


def calculate_impact_tool(args):
    _LOGGER.info("Starting impact calculation")

    files_set = find_files(args.dir, args.extlist)
    if args.file:
        files_set.add(args.file)
    if args.files:
        files_set.update(args.files)

    input_config_path = args.config
    output_dir_path = args.outputdir
    params_space_path = args.paramsspace
    override_def_params_space = args.overridedefparamsspace
    ignore_params = args.ignoreparams
    consider_params = args.considerparams
    calculate_impact(
        files_set,
        input_config_path,
        output_dir_path,
        params_space_path=params_space_path,
        override_def_params_space=override_def_params_space,
        ignore_params=ignore_params,
        consider_params=consider_params,
    )
    _LOGGER.info("Completed")


# =============================================================


# ext_list - with dot if needed
def find_files(search_dir, ext_list):
    ret_set = set()
    for ext_item in ext_list:
        for filename in glob(f"{search_dir}/**/*{ext_item}", recursive=True):
            ret_set.add(filename)
    return ret_set


# =============================================================


def main():
    parser = argparse.ArgumentParser(
        prog="python3 -m uncrustimpact",
        description="display uncrustify configuration impact on given source files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    parser.add_argument("--listtools", action="store_true", help="List tools")
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(help="one of tools", description="use one of tools", dest="tool", required=False)

    ## =================================================

    description = "generate parameters space dict"
    subparser = subparsers.add_parser(
        "genparamsspace", help=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparser.description = description
    subparser.set_defaults(func=gen_params_space_dict_tool)

    ## =================================================

    description = "calculate config impact"
    subparser = subparsers.add_parser(
        "impact", help=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparser.description = description
    subparser.set_defaults(func=calculate_impact_tool)
    subparser.add_argument("--file", action="store", help="File to analyze")  # backward compatibility
    subparser.add_argument("-f", "--files", nargs="+", default=[], help="Files to analyze")
    subparser.add_argument("-d", "--dir", action="store", help="Path to directory to search for files")
    subparser.add_argument(
        "--extlist",
        nargs="+",
        default=[".h", ".hpp", ".c", "cpp"],
        help="List of extensions to look for (in case of --dir)",
    )
    subparser.add_argument("-c", "--config", action="store", required=True, help="Base uncrustify config")
    subparser.add_argument("-od", "--outputdir", action="store", required=True, help="Output directory")
    subparser.add_argument("-ps", "--paramsspace", action="store", help="Path to params space config JSON")
    subparser.add_argument(
        "-odps", "--overridedefparamsspace", action="store_true", help="Override default params space with given one"
    )
    subparser.add_argument("-ip", "--ignoreparams", nargs="+", default=[], help="Parameters list to ignore")
    subparser.add_argument("-cp", "--considerparams", nargs="+", default=[], help="Parameters list to consider")

    ## =================================================

    args = parser.parse_args()

    if args.listtools is True:
        tools_list = list(subparsers.choices.keys())
        print(", ".join(tools_list))
        return 0

    logging.basicConfig()
    if args.logall is True:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    if not args.func:
        ## no command given -- print help message
        parser.print_help()
        sys.exit(1)
        return 1

    args.func(args)
    return 0


## ============================= main section ===================================


if __name__ == "__main__":
    EXIT_CODE = main()
    sys.exit(EXIT_CODE)
