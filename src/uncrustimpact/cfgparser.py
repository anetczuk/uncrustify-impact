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


def prepare_params_space_dict(params_space_path=None, override_def_params_space=False):
    params_space_dict = None
    if params_space_path:
        params_space_dict = load_params_space_json(params_space_path)
        if override_def_params_space:
            def_space_dict = get_default_params_space()
            params_space_dict = {**def_space_dict, **params_space_dict}
    else:
        params_space_dict = get_default_params_space()
    return params_space_dict


def get_default_params_space():
    default_cfg_path = "/tmp/uncrustify_show-config.txt"  # nosec
    generate_default_config(default_cfg_path)
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
        cfg_line = CfgLine(line)
        if not cfg_line.name:
            if cfg_line.comment:
                recent_comments += "#" + cfg_line.comment
                # recent_comments += "#" + cfg_line.comment.rstrip() + "\n"
            else:
                # empty line
                recent_comments = ""
            continue

        name = cfg_line.name
        value = cfg_line.value
        comment = ""
        if cfg_line.comment:
            comment = cfg_line.comment.strip()

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

        value = convert_value(value, param_type)

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


def convert_value(value_str, value_type: ParamType):
    if value_type is None:
        return value_str

    if value_type is ParamType.STRING:
        return value_str
    if value_type is ParamType.INTEGER:
        return int(value_str)
    if value_type is ParamType.UNSIGNED:
        return int(value_str)
    if value_type is ParamType.SET:
        return value_str

    raise RuntimeError(f"unknown type: {value_type}")


## ========================================================


def read_config_content(config_path):
    if not config_path:
        # read default config
        config_path = "/tmp/uncrustify_show-config.txt"  # nosec
        generate_default_config(config_path)

    # read lines
    with open(config_path, encoding="utf-8") as item_file:
        return item_file.readlines()


def generate_default_config(config_path):
    error_code = os.system(f"uncrustify --show-config > {config_path}")  # nosec
    if error_code != 0:
        raise RuntimeError("unable to execute uncrustify")


def modify_config_params(config_lines, params_dict):
    ret_list = []
    for line in config_lines:
        cfg_line = CfgLine(line)
        if not cfg_line.name:
            ret_list.append(line)
            continue
        param_value = params_dict.get(cfg_line.name)
        if param_value is None:
            continue
        cfg_line.value = str(param_value)
        new_line = cfg_line.join()
        ret_list.append(new_line)
    return ret_list


def write_config_content(out_cfg_path, config_lines):
    with open(out_cfg_path, "w", encoding="utf-8") as out_file:
        out_file.writelines(config_lines)


## ========================================================


def read_cfg_to_dict(cfg_path, params_space_dict=None):
    if params_space_dict is None:
        params_space_dict = {}
    with open(cfg_path, encoding="utf-8") as item_file:
        lines_list = item_file.readlines()

    all_params_dict = {}

    for line in lines_list:
        cfg_line = CfgLine(line)
        if cfg_line.is_valid() is False:
            continue

        param_def = params_space_dict.get(cfg_line.name, {})
        value_type = param_def.get("type")
        value = convert_value(cfg_line.value, value_type)

        all_params_dict[cfg_line.name] = value

    return all_params_dict


class CfgLine:
    def __init__(self, line_string):
        self.space0 = None
        self.name = None
        self.space1 = None
        # equal sign goes between space1 and space2
        self.space2 = None
        self.value = None
        self.space3 = None
        self.comment = None

        self._parse(line_string)

    def _parse(self, cfg_line):
        self.space0, line = split_leading_spaces(cfg_line)
        if not line:
            # empty line
            return
        if line.startswith("#"):
            # comment line
            self.comment = line[1:]
            return
        name_val = line.split("=")
        self.name, self.space1 = split_trailing_spaces(name_val[0])
        self.space2, val_comm = split_leading_spaces(name_val[1])
        val_comm = val_comm.split("#")
        self.value, self.space3 = split_trailing_spaces(val_comm[0])
        if len(val_comm) > 1:
            self.comment = val_comm[1]

    def is_valid(self):
        return bool(self.name)

    def join(self):
        ret_str = ""
        if self.space0:
            ret_str += self.space0
        if self.name:
            ret_str += self.name
            if self.space1:
                ret_str += self.space1
            ret_str += "="
        if self.space2:
            ret_str += self.space2
        if self.value:
            ret_str += self.value
        if self.space3:
            ret_str += self.space3
        if self.comment:
            ret_str += "#" + self.comment
        return ret_str


def split_leading_spaces(data_string):
    stripped = data_string.lstrip()
    length = len(data_string) - len(stripped)
    return (data_string[:length], stripped)


def split_trailing_spaces(data_string):
    stripped = data_string.rstrip()
    length = len(stripped)
    return (stripped, data_string[length:])


def write_dict_to_cfg(params_dict, out_path):
    with open(out_path, "w", encoding="utf-8") as out_file:
        content = ""
        for param_name, param_val in params_dict.items():
            content += f"""{param_name} = {param_val}\n"""
        out_file.write(content)


## ========================================================


def is_cfg_valid(cfg_dict):
    nl_max = cfg_dict.get("nl_max")
    if nl_max is None:
        return True
    nl_func_var_def_blk = cfg_dict.get("nl_func_var_def_blk")
    if nl_max > 0:
        if nl_func_var_def_blk is None:
            return True
        if nl_func_var_def_blk >= nl_max:
            return False
    return True
