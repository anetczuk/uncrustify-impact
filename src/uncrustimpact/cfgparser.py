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

import re
import json


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@unique
class ParamType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    UNSIGNED = "unsigned"
    SET = "set"


def print_params_space():
    params_space_dict = get_default_params_space()
    for subdict in params_space_dict.values():
        subdict["type"] = str(subdict["type"])
    json.dump(params_space_dict, sys.stdout, indent=4)


def get_default_params_space():
    default_cfg_path = "/tmp/uncrustify_show-config.txt"  # nosec
    error_code = os.system(f"uncrustify --show-config > {default_cfg_path}")  # nosec
    if error_code != 0:
        raise RuntimeError("unable to execute uncrustify")
    return read_params_space(default_cfg_path)


def load_params_space_json(params_space_path):
    type_name = "ParamType"
    type_name += "."
    with open(params_space_path, encoding="utf-8") as space_file:
        loaded_dict = json.load(space_file)
        for param_def in loaded_dict.values():
            param_type = param_def["type"]
            if not param_type.startswith(type_name):
                raise RuntimeError(f"invalid type value: {param_type}")
            param_type = param_type[len(type_name) :]
            param_def["type"] = ParamType[param_type]
        return loaded_dict


def read_params_space(cfg_path):
    with open(cfg_path, encoding="utf-8") as item_file:
        lines_list = item_file.readlines()

    all_params_dict = {}

    recent_comments = ""

    for line in lines_list:
        line = line.strip()
        if not line:
            # empty line
            recent_comments = ""
            continue
        if line.startswith("#"):
            # comment line
            recent_comments += line + "\n"
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
            value = int(value)
        elif comment == "unsigned number":
            param_type = ParamType.UNSIGNED
            value = int(value)
            allowed_set = read_doc_set(recent_comments)  # sometimes there is limited number of values
            if allowed_set is not None:
                param_type = ParamType.SET
        elif "/" in comment:
            param_type = ParamType.SET
            allowed_set = comment.split("/")
        else:
            raise RuntimeError(f"unknown type: {comment} example value: {value}")

        param_dict = {"value": value, "type": param_type, "allowed": allowed_set, "doc": recent_comments, "line": line}
        all_params_dict[name] = param_dict

        recent_comments = ""

    return all_params_dict


def read_doc_set(doc_string):
    allowed = []
    for line in doc_string.split("\n"):
        found = re.match(r"#\s(\S):.*?", line)
        if found is not None:
            allowed.append(found.group(1))
    if allowed:
        if allowed[-1] == "Default":
            del allowed[-1]
    if allowed:
        return sorted(allowed)
    return None


def write_dict_to_cfg(params_dict, out_path):
    with open(out_path, "w", encoding="utf-8") as out_file:
        content = ""
        for param_name, param_val in params_dict.items():
            content += f"""{param_name} = {param_val}\n"""
        out_file.write(content)
