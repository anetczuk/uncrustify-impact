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
import re
from collections import Counter
import json

from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

# from uncrustimpact.multiprocessingmock import DummyPool as Pool
# from uncrustimpact.multiprocessingmock import DummyPool as ThreadPool

from uncrustimpact.filediff import Changes
from uncrustimpact.cfgparser import (
    get_default_params_space,
    read_params_space,
    write_dict_to_cfg,
    ParamType,
    load_params_space_json,
)
from uncrustimpact.printhtml import print_to_html, print_param_page, generate_params_stats, print_files_page


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


def execute_uncrustify(input_file_path, input_config_path, out_file_path):
    command = f"uncrustify -q -c {input_config_path} --no-backup -f {input_file_path} -o {out_file_path}"
    error_code = os.system(command)  # nosec
    if error_code != 0:
        _LOGGER.error("unable to execute command: %s", command)
        raise RuntimeError("unable to execute uncrustify")


def calculate_impact(
    input_base_file_set,
    base_config_path,
    output_base_dir_path,
    params_space_path=None,
    override_def_params_space=False,
    ignore_params=None,
    consider_params=None,
):
    os.makedirs(output_base_dir_path, exist_ok=True)

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

    _LOGGER.info("generating config files")
    param_list = generate_config_files(
        base_config_path, output_base_dir_path, params_space_dict, ignore_params, consider_params
    )
    params_list_path = os.path.join(output_base_dir_path, "config", "params_list.json")
    with open(params_list_path, mode="w", encoding="utf-8") as params_file:
        json.dump(param_list, params_file)

    path_prefix_len = get_common_prefix_len(input_base_file_set)

    _LOGGER.info("calculating files impact")
    unused_cfg_counter = Counter()
    files_stats = {}
    with Pool() as process_pool:
        result_queue = []

        for file_path in input_base_file_set:
            file_rel_path = file_path[path_prefix_len:]
            file_dir_name = convert_path(file_rel_path)
            file_dir_path = os.path.join(output_base_dir_path, file_dir_name)

            # execute uncrustify in separate thread
            async_result = process_pool.apply_async(
                calculate_impact_file, [file_path, base_config_path, params_list_path, file_dir_path]
            )
            result_queue.append((file_rel_path, async_result))

        # wait for results
        for file_rel_path, async_result in result_queue:
            file_index_path, param_stats, unused_configs = async_result.get()
            files_stats[file_rel_path] = (file_index_path, sum(param_stats.values()))
            unused_cfg_counter.update(unused_configs)

    # remove unused configs
    _LOGGER.info("removing unused configs")
    total_files = len(input_base_file_set)
    for cfg_path, cfg_count in unused_cfg_counter.items():
        if cfg_count >= total_files:
            os.remove(cfg_path)

    files_stats = dict(sorted(files_stats.items(), key=lambda item: (-item[1][1], item[0])))

    out_path = os.path.join(output_base_dir_path, "index.html")
    _LOGGER.info("writing main page in file://%s", out_path)
    print_files_page(files_stats, out_path)


def calculate_impact_file(input_base_file_path, base_config_path, param_list, output_base_dir_path):
    _LOGGER.info("handling file %s", input_base_file_path)

    if isinstance(param_list, str):
        with open(param_list, encoding="utf-8") as params_file:
            param_list = json.load(params_file)

    params_dir_path = os.path.join(output_base_dir_path, "params")
    os.makedirs(params_dir_path, exist_ok=True)
    input_filename = os.path.basename(input_base_file_path)

    # setting extension to .txt changes results
    base_file_path = os.path.join(output_base_dir_path, input_filename)
    execute_uncrustify(input_base_file_path, base_config_path, base_file_path)

    generate_file_variants(base_file_path, param_list, params_dir_path)

    _LOGGER.info("calculating stats for file %s", input_base_file_path)

    with open(base_file_path, encoding="utf-8") as file_1:
        filebase_text = file_1.readlines()

    changes = Changes("base", filebase_text)

    params_stats = {}

    unused_configs = []
    for param_item in param_list:
        param_name = param_item[0]
        param_def = param_item[1]
        param_values = param_item[2]
        base_param_value = param_item[3]

        param_val_list = []

        for param_data in param_values:
            param_val = param_data[0]
            param_id = param_data[1]
            out_cfg_path = param_data[2]
            out_filename = f"{param_id}.txt"
            out_file_path = os.path.join(params_dir_path, out_filename)

            with open(out_file_path, encoding="utf-8") as item_file:
                item_text = item_file.readlines()
            raw_diff = changes.calculate_diff(item_text)
            changed = changes.parse_diff(param_name, raw_diff)

            if not changed:
                # remove unused files
                # os.remove(out_cfg_path)
                unused_configs.append(out_cfg_path)
                os.remove(out_file_path)
                continue

            # write files diff to file
            raw_diff = "".join(raw_diff)
            diff_filename = name_to_diff_filename(param_id)
            out_diff_path = os.path.join(params_dir_path, diff_filename)
            with open(out_diff_path, "w", encoding="utf-8") as out_file:
                out_file.write(raw_diff)

            cfg_relative_path = os.path.relpath(out_cfg_path, params_dir_path)
            param_val_list.append((param_val, cfg_relative_path, out_filename, diff_filename))

        param_changes = changes.count_changes(param_name)
        params_stats[param_name] = param_changes

        # write parameter page
        print_param_page(param_name, param_val_list, base_param_value, param_def, param_changes, params_dir_path)

    # changes.print_diff()

    top_content = f"""\
<div><b>Base file:</b> <a href="{input_filename}">{input_filename}</a></div>
"""

    params_stats = dict(sorted(params_stats.items(), key=lambda item: (-item[1], item[0])))

    total_changes = changes.count_changed_lines()
    bottom_content = f"""
<div class="section">Lines changed: {total_changes}</div>
"""
    bottom_content += generate_params_stats(params_stats, label_to_link=label_to_link)

    # write general diff
    content = print_to_html(
        changes, label_converter=labels_to_links, top_content=top_content, bottom_content=bottom_content
    )
    out_path = os.path.join(output_base_dir_path, "index.html")
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)

    _LOGGER.info("output stored to: file://%s", out_path)
    return out_path, params_stats, unused_configs


def generate_config_files(
    base_config_path, output_base_dir_path, params_space_dict=None, ignore_params=None, consider_params=None
):
    params_dir_path = os.path.join(output_base_dir_path, "config")
    os.makedirs(params_dir_path, exist_ok=True)

    ignore_params_set = set()
    if ignore_params:
        ignore_params_set = set(ignore_params)

    consider_params_set = set()
    if consider_params:
        consider_params_set = set(consider_params)

    params_base_cfg_dict = read_params_space(base_config_path)
    # pprint.pprint(params_base_cfg_dict)
    ## convert to standard config dict
    params_base_cfg_dict = {key: subdict["value"] for key, subdict in params_base_cfg_dict.items()}

    param_list = []
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

        params_data = []
        for param_val in param_values:
            param_id = f"{param_name}-{param_val}"
            out_cfg_path = os.path.join(params_dir_path, f"{param_id}.cfg")
            params_data.append((param_val, param_id, out_cfg_path))

            curr_cfg_dict = copy.copy(params_base_cfg_dict)
            # curr_cfg_dict = copy.deepcopy(params_base_cfg_dict)
            curr_cfg_dict[param_name] = param_val

            # execute uncrustify in separate thread
            write_dict_to_cfg(curr_cfg_dict, out_cfg_path)

        param_list.append((param_name, param_def, params_data, base_param_value))

    return param_list


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
    raise RuntimeError(f"unahandled param type: {param_type} {type(param_type)}")


def generate_file_variants(input_file_path, param_list, output_dir):
    tasks_data = []
    for param_item in param_list:
        param_values = param_item[2]

        for param_data in param_values:
            param_id = param_data[1]
            input_cfg_path = param_data[2]
            out_file_path = os.path.join(output_dir, f"{param_id}.txt")
            tasks_data.append([input_file_path, input_cfg_path, out_file_path])

    with ThreadPool() as process_pool:
        process_pool.starmap(execute_uncrustify, tasks_data)


def labels_to_links(labels_list):
    if not labels_list:
        return labels_list
    links_list = []
    for item in labels_list:
        if not item:
            continue
        link = label_to_link(item)
        links_list.append(link)
    if not links_list:
        return None
    return links_list


def label_to_link(label):
    return f"""<a href="./params/{label}.html">{label}</a>"""


def name_to_diff_filename(name):
    return f"{name}.diff.txt"


def convert_path(file_path):
    file_dir_name = copy.deepcopy(file_path)
    file_dir_name = file_dir_name.replace(".", "_")
    file_dir_name = file_dir_name.replace("/", "_")
    file_dir_name = file_dir_name.replace("\\", "_")
    file_dir_name = re.sub(r"\s+", "_", file_dir_name)  # replace all whitespaces
    return file_dir_name


def get_common_prefix_len(string_list):
    list_len = len(string_list)
    if list_len > 1:
        path_prefix = os.path.commonprefix(list(string_list))
        return len(path_prefix)
    if list_len > 0:
        first_item = list(string_list)[0]
        return len(os.path.dirname(first_item)) + 1  # include dir slash
    return 0
