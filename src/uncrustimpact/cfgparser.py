#!/usr/bin/env python3
#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import os
from enum import Enum, unique

import json


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@unique
class ParamType(Enum):
    STRING = "string"
    INTEGER = "integer"
    UNSIGNED = "unsigned"
    SET = "set"


def print_params_space():
    default_cfg_path = "/tmp/uncrustify_show-config.txt"  # nosec
    error_code = os.system(f"uncrustify --show-config > {default_cfg_path}")  # nosec
    if error_code != 0:
        raise RuntimeError("unable to execute uncrustify")

    params_dict = read_params_space(default_cfg_path)
    json.dump(params_dict, sys.stdout, indent=4)


def read_params_space(cfg_path):
    with open(cfg_path, encoding="utf-8") as item_file:
        lines_list = item_file.readlines()

    all_params_dict = {}

    for line in lines_list:
        line = line.strip()
        if not line:
            # empty line
            continue
        if line.startswith("#"):
            # comment line
            continue
        name_val = line.split("=")
        name = name_val[0]
        name = name.strip()
        val_comm = name_val[1]
        val_comm = val_comm.strip()
        val_comm = val_comm.split("#")
        value = val_comm[0]
        value = value.strip()
        comment = val_comm[1]
        comment = comment.strip()

        param_type = None
        allowed_set = None
        if comment == "string":
            param_type = ParamType.STRING
        elif comment == "number":
            param_type = ParamType.INTEGER
        elif comment == "unsigned number":
            param_type = ParamType.UNSIGNED
        elif "/" in comment:
            param_type = ParamType.SET
            allowed_set = comment.split("/")
        else:
            raise RuntimeError(f"unknown type: {comment} example value: {value}")

        param_dict = {"value": value, "type": str(param_type), "allowed": allowed_set, "line": line}
        all_params_dict[name] = param_dict

    return all_params_dict
