#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging
import copy

# import random

from uncrustimpact.diff import Changes
from uncrustimpact.cfgparser import get_default_params_space, read_params_space, write_dict_to_cfg, ParamType,\
    load_params_space_json
from uncrustimpact.printhtml import print_to_html, print_param_page, generate_params_stats


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


def execute_uncrustify(input_file_path, base_config_path, out_file_path):
    command = f"uncrustify -q -c {base_config_path} --no-backup -f {input_file_path} -o {out_file_path}"
    error_code = os.system(command)  # nosec
    if error_code != 0:
        _LOGGER.error("unable to execute command: %s", command)
        raise RuntimeError("unable to execute uncrustify")


def calculate_impact(
    input_base_file_path,
    base_config_path,
    output_base_dir_path,
    params_space_path=None,
    override_def_params_space=False,
    ignore_params=None,
    consider_params=None,
):
    uncrust_dir_path = os.path.join(output_base_dir_path, "uncrustify")
    os.makedirs(uncrust_dir_path, exist_ok=True)
    input_filename = os.path.basename(input_base_file_path)

    # setting extension to .txt changes results
    base_file_path = os.path.join(output_base_dir_path, input_filename)
    execute_uncrustify(input_base_file_path, base_config_path, base_file_path)

    ignore_params_set = set()
    if ignore_params:
        ignore_params_set = set(ignore_params)

    consider_params_set = set()
    if consider_params:
        consider_params_set = set(consider_params)

    # if random_seed is not None:
    #     random.seed(random_seed)

    with open(base_file_path, encoding="utf-8") as file_1:
        filebase_text = file_1.readlines()

    params_base_cfg_dict = read_params_space(base_config_path)
    # pprint.pprint(params_base_cfg_dict)
    ## convert to standard config dict
    params_base_cfg_dict = {key: subdict["value"] for key, subdict in params_base_cfg_dict.items()}

    changes = Changes("base", filebase_text)

    params_space_dict = None
    if params_space_path:
        _LOGGER.info("using params space from file: %s", params_space_path)
        params_space_dict = load_params_space_json(params_space_path)
        if override_def_params_space:
            def_space_dict = get_default_params_space()
            params_space_dict = {**def_space_dict, **params_space_dict}
    else:
        _LOGGER.info("using default params space")
        params_space_dict = get_default_params_space()

    params_stats = {}

    for param_name, param_def in params_space_dict.items():
        if param_name in ignore_params_set:
            # ignore parameter
            continue
        if consider_params_set:
            if param_name not in consider_params_set:
                # ignore parameter
                continue

        base_param_value = params_base_cfg_dict.get(param_name)
        param_values = generate_param_values(base_param_value, param_def)
        if not param_values:
            # params not changed -- skip
            continue

        param_val_list = []
        for param_val in param_values:
            param_id = f"{param_name}-{param_val}"
            params_base_cfg_dict[param_name] = param_val

            out_cfg_path = os.path.join(uncrust_dir_path, f"{param_id}.cfg")
            write_dict_to_cfg(params_base_cfg_dict, out_cfg_path)

            out_file_path = os.path.join(uncrust_dir_path, f"{param_id}.txt")
            execute_uncrustify(base_file_path, out_cfg_path, out_file_path)

            with open(out_file_path, encoding="utf-8") as item_file:
                item_text = item_file.readlines()
            raw_diff = changes.calculate_diff(item_text)
            changed = changes.parse_diff(param_name, raw_diff)

            if not changed:
                # remove unused files
                os.remove(out_cfg_path)
                os.remove(out_file_path)
                continue

            # write files diff to file
            raw_diff = "".join(raw_diff)
            diff_filename = name_to_diff_filename(param_id)
            out_diff_path = os.path.join(uncrust_dir_path, diff_filename)
            with open(out_diff_path, "w", encoding="utf-8") as out_file:
                out_file.write(raw_diff)

            param_val_list.append((param_val, param_id, diff_filename))

        # restore input value
        params_base_cfg_dict[param_name] = base_param_value

        param_changes = changes.count_changes(param_name)
        params_stats[param_name] = param_changes

        # write parameter page
        print_param_page(param_name, param_val_list, base_param_value, param_def, param_changes, uncrust_dir_path)

    # changes.print_diff()

    top_content = f"""\
<div><b>Base file:</b> <a href="{base_file_path}">{base_file_path}</a></div>
"""

    params_stats = dict(sorted(params_stats.items(), key=lambda item: (-item[1], item[0])))
    bottom_content = generate_params_stats(params_stats, label_to_link=label_to_link)

    # write general diff
    content = print_to_html(
        changes, label_converter=labels_to_links, top_content=top_content, bottom_content=bottom_content
    )
    out_path = os.path.join(output_base_dir_path, "index.html")
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)

    _LOGGER.info("output stored to: file://%s", out_path)


def generate_param_values(curr_param_value, param_def_dict):
    # pprint.pprint(param_def_dict, indent=4, sort_dicts=False)
    param_type = param_def_dict["type"]
    if param_type == ParamType.STRING:
        return None
    if param_type == ParamType.INTEGER:
        return [curr_param_value + 1]
    if param_type == ParamType.UNSIGNED:
        return [curr_param_value + 1]
    if param_type == ParamType.SET:
        allowed_values = param_def_dict["allowed"]
        if not allowed_values:
            raise RuntimeError("invalid 'allowed' value for parameter definition")
        allowed_list = copy.deepcopy(allowed_values)
        if curr_param_value in allowed_list:
            allowed_list.remove(curr_param_value)
        if not allowed_list:
            return None
        return list(allowed_list)
    raise RuntimeError(f"unahandled param type: {param_type}")


def labels_to_links(labels_list):
    if not labels_list:
        return labels_list
    links_list = []
    for item in labels_list:
        link = label_to_link(item)
        links_list.append(link)
    return links_list


def label_to_link(label):
    return f"""<a href="./uncrustify/{label}.html">{label}</a>"""


def name_to_diff_filename(name):
    return f"{name}.diff.txt"
