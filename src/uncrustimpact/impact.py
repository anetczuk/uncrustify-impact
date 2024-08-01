#!/usr/bin/env python3
#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import copy
import json
import random

from uncrustimpact.diff import Changes
from uncrustimpact.cfgparser import get_default_params_space, read_params_space, write_dict_to_cfg, ParamType
from uncrustimpact.printhtml import print_to_html


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def execute_uncrustify(input_file_path, base_config_path, out_file_path):
    error_code = os.system(f"uncrustify -q -c {base_config_path} -f {input_file_path} -o {out_file_path}")  # nosec
    if error_code != 0:
        raise RuntimeError("unable to execute uncrustify")


def calculate_impact(
    base_file_path, base_config_path, output_base_dir_path, params_space_path=None, ignore_params=None, randomseed=None
):
    uncrust_dir_path = os.path.join(output_base_dir_path, "uncrustify")
    os.makedirs(uncrust_dir_path, exist_ok=True)
    # input_filename = os.path.basename(base_file_path)

    ignore_params_set = set()
    if ignore_params:
        ignore_params_set = set(ignore_params)

    if randomseed is not None:
        random.seed(randomseed)

    with open(base_file_path, encoding="utf-8") as file_1:
        filebase_text = file_1.readlines()

    params_base_cfg_dict = read_params_space(base_config_path)
    # pprint.pprint(params_base_cfg_dict)

    changes = Changes("base", filebase_text)

    params_space_dict = None
    if params_space_path:
        with open(params_space_path, encoding="utf-8") as space_file:
            params_space_dict = json.load(space_file)
    else:
        params_space_dict = get_default_params_space()

    for param_name, param_data in params_space_dict.items():
        if param_name in ignore_params_set:
            # ignore parameter
            continue

        curr_cfg = copy.deepcopy(params_base_cfg_dict)
        if modify_cfg(curr_cfg, param_name, param_data) is False:
            # params not changed -- skip
            continue

        out_cfg_path = os.path.join(uncrust_dir_path, f"{param_name}.cfg")
        write_dict_to_cfg(curr_cfg, out_cfg_path)

        out_file_path = os.path.join(uncrust_dir_path, f"{param_name}.txt")
        execute_uncrustify(base_file_path, out_cfg_path, out_file_path)

        with open(out_file_path, encoding="utf-8") as item_file:
            item_text = item_file.readlines()
        changes.add_diff(param_name, item_text)

        raw_diff = changes.calculate_diff(item_text)
        raw_diff = "".join(raw_diff)
        diff_filename = name_to_diff_filename(param_name)
        out_diff_path = os.path.join(uncrust_dir_path, diff_filename)
        with open(out_diff_path, "w", encoding="utf-8") as out_file:
            out_file.write(raw_diff)

    content = print_to_html(changes, label_converter=labels_to_links)
    out_path = os.path.join(output_base_dir_path, "index.html")
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)


def modify_cfg(cfg_dict, param_name, param_def_dict):
    param_cfg_dict = cfg_dict.get(param_name)
    if param_cfg_dict is None:
        return False
    # pprint.pprint(param_def_dict, indent=4, sort_dicts=False)
    param_type = param_def_dict["type"]
    if param_type == str(ParamType.STRING):
        return False
    if param_type == str(ParamType.INTEGER):
        value_str = param_cfg_dict["value"]
        value = int(value_str)
        value += 1
        param_cfg_dict["value"] = str(value)
        return True
    if param_type == str(ParamType.UNSIGNED):
        value_str = param_cfg_dict["value"]
        value = int(value_str)
        value += 1
        param_cfg_dict["value"] = str(value)
        return True
    if param_type == str(ParamType.SET):
        allowed_values = param_def_dict["allowed"]
        if not allowed_values:
            raise RuntimeError(f"invalid 'allowed' value for parameter definition: {param_name}")
        value_str = param_cfg_dict["value"]
        allowed_values.remove(value_str)
        if not allowed_values:
            return False
        new_value = random.sample(allowed_values, 1)
        new_value = new_value[0]
        param_cfg_dict["value"] = str(new_value)
        return True
    raise RuntimeError(f"unahandled param type: {param_type}")


def labels_to_links(labels_list):
    if not labels_list:
        return labels_list
    links_list = []
    for item in labels_list:
        diff_filename = name_to_diff_filename(item)
        link = f"""<a href="./uncrustify/{diff_filename}">{item}</a>"""
        links_list.append(link)
    return links_list


def name_to_diff_filename(name):
    return f"{name}.diff.txt"
