#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging

import shutil
from multiprocessing import Pool

# from multiprocessing.pool import ThreadPool

# from uncrustimpact.multiprocessingmock import DummyPool as Pool
from uncrustimpact.multiprocessingmock import DummyPool as ThreadPool

from uncrustimpact.filediff import Changes
from uncrustimpact.cfgparser import (
    prepare_params_space_dict,
    read_config_content,
    modify_config_params,
    write_config_content,
)
from uncrustimpact.printhtml import print_fit_page, print_fitparam_page
from uncrustimpact.impacttool import generate_config_files, get_common_prefix_len, convert_path, execute_uncrustify
from uncrustimpact.difftool import print_diff_page


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


def calculate_fit(
    input_base_file_set,
    base_config_path,
    output_base_dir_path,
    params_space_path=None,
    override_def_params_space=False,
    ignore_params=None,
    consider_params=None,
):
    os.makedirs(output_base_dir_path, exist_ok=True)

    params_space_dict = prepare_params_space_dict(params_space_path, override_def_params_space)

    _LOGGER.info("using input config: %s", base_config_path)
    _LOGGER.info("generating config files")
    output_config_dir_path = os.path.join(output_base_dir_path, "config")
    param_list = generate_config_files(
        base_config_path,
        output_config_dir_path,
        params_space_dict,
        ignore_params,
        consider_params,
        include_default_value=True,
        subdir_id=True,
    )

    out_param_dir_path = os.path.join(output_base_dir_path, "params")

    _LOGGER.info("calculating files fit")
    best_fit = {}
    with Pool() as process_pool:
        result_queue = []

        for param_item in param_list:
            param_values = param_item[2]

            param_variants = []

            for param_single_val in param_values:
                async_result = process_pool.apply_async(
                    calculate_fit_param, [param_single_val, input_base_file_set, out_param_dir_path]
                )

                param_variants.append((param_single_val, async_result))

            result_queue.append((param_item, param_variants))

        # wait for results
        for param_item, param_variants in result_queue:
            if not param_variants:
                continue
            # collect and process param results
            param_results = []
            min_val = float("inf")
            max_val = float("-inf")
            for param_data, async_result in param_variants:
                param_changes_counter = async_result.get()
                min_val = min(min_val, param_changes_counter)
                max_val = max(max_val, param_changes_counter)
                param_results.append((param_changes_counter, param_data))
            min_results = [item for item in param_results if item[0] == min_val]
            result_dict = {item[1][0]: item[1][2] for item in min_results}
            best_values = [str(item) for item in result_dict.keys()]

            cfg_value = param_item[3]
            best_value = cfg_value
            is_changed = False
            if min_val != max_val:
                # there is impact of the parameter
                if str(cfg_value) not in best_values:
                    # config value is not the best value
                    is_changed = True

                    param_def = param_item[1]
                    default_value = param_def["value"]
                    if str(default_value) not in best_values:
                        best_value = min_results[0][1][0]  # first value
                    else:
                        best_value = default_value
            # else:  # parameter does not have any impact -- ignore

            # print param results
            param_name = param_item[0]
            param_results = sorted(param_results, key=lambda item: item[1][0])  # sort by parameter value
            out_param_page_path = os.path.join(out_param_dir_path, param_name, "index.html")
            print_fitparam_page(param_item, best_value, param_results, out_param_page_path)

            best_fit[param_name] = (best_value, is_changed, min_val, out_param_page_path, out_param_dir_path)

    best_cfg_name = "best_config.cfg"
    params_dict = {key: item[0] for key, item in best_fit.items()}
    best_cfg_path = os.path.join(output_base_dir_path, best_cfg_name)
    # write_dict_to_cfg(params_dict, best_cfg_path)
    base_config_content = read_config_content(base_config_path)
    best_config_content = modify_config_params(base_config_content, params_dict)
    write_config_content(best_cfg_path, best_config_content)

    out_path = os.path.join(output_base_dir_path, "index.html")
    _LOGGER.info("writing main page in file://%s", out_path)
    best_fit = dict(sorted(best_fit.items()))
    print_fit_page(best_cfg_name, best_fit, out_path)

    # cleanup
    shutil.rmtree(output_config_dir_path)
    for param_name, item in best_fit.items():
        is_changed = item[1]
        if is_changed:
            continue
        out_param_file = item[3]
        if os.path.exists(out_param_file):
            os.remove(out_param_file)
        out_param_dir = os.path.join(item[4], param_name)
        if os.path.isdir(out_param_dir):
            shutil.rmtree(out_param_dir)


def calculate_fit_param(param_data, input_file_path_set, output_base_dir_path):
    # _LOGGER.info("handling parameter %s", param_name)

    path_prefix_len = get_common_prefix_len(input_file_path_set)

    param_changes_counter = 0

    param_id = param_data[1]  # param name and value
    input_cfg_path = param_data[2]

    param_dir_path = os.path.join(output_base_dir_path, param_id)
    os.makedirs(param_dir_path, exist_ok=True)

    with ThreadPool() as process_pool:
        result_queue = []
        for input_file_path in input_file_path_set:
            file_rel_path = input_file_path[path_prefix_len:]
            file_dir_name = convert_path(file_rel_path)
            out_file_path = os.path.join(param_dir_path, file_dir_name)

            async_result = process_pool.apply_async(
                execute_uncrustify, [input_file_path, input_cfg_path, out_file_path]
            )
            result_queue.append((input_file_path, out_file_path, async_result))

        # wait for results
        for input_file_path, out_file_path, async_result in result_queue:
            async_result.get()

            with open(input_file_path, encoding="utf-8") as file_1:
                filebase_text = file_1.readlines()
            changes = Changes("base", filebase_text)

            with open(out_file_path, encoding="utf-8") as item_file:
                item_text = item_file.readlines()
            raw_diff = changes.calculate_diff(item_text)
            changes.parse_diff(None, raw_diff)
            # changes.parse_diff("change", raw_diff)

            # write files diff to file
            # diff_filename = name_to_diff_filename(param_id)
            out_diff_path = os.path.join(param_dir_path, "diff.txt")
            raw_diff = "".join(raw_diff)
            with open(out_diff_path, "w", encoding="utf-8") as out_file:
                out_file.write(raw_diff)

            out_diff_page_path = os.path.join(param_dir_path, "index.html")
            input_filename = os.path.basename(out_file_path)
            print_diff_page(changes, out_diff_page_path, input_filename)

            param_changes = changes.count_changes()
            param_changes_counter += param_changes

    return param_changes_counter
