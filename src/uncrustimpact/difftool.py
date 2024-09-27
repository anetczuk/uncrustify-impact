#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging

# import random

from multiprocessing import Pool

from uncrustimpact.filediff import Changes
from uncrustimpact.cfgparser import read_params_space
from uncrustimpact.printhtml import print_to_html, print_impact_page
from uncrustimpact.impacttool import (
    labels_to_links,
    name_to_diff_filename,
    execute_uncrustify,
    convert_path,
    get_common_prefix_len,
)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


def calculate_diff(input_base_file_set, base_config_path, output_base_dir_path):
    os.makedirs(output_base_dir_path, exist_ok=True)

    path_prefix_len = get_common_prefix_len(input_base_file_set)

    files_stats = {}
    with Pool() as process_pool:
        result_queue = []

        for file_path in input_base_file_set:
            file_rel_path = file_path[path_prefix_len:]
            file_dir_name = convert_path(file_rel_path)
            file_dir_path = os.path.join(output_base_dir_path, file_dir_name)

            # execute uncrustify in separate thread
            async_result = process_pool.apply_async(calculate_diff_file, [file_path, base_config_path, file_dir_path])
            result_queue.append((file_rel_path, async_result))

        # wait for results
        for file_rel_path, async_result in result_queue:
            file_index_path, changes_num = async_result.get()
            if file_index_path is None or changes_num is None:
                continue
            files_stats[file_rel_path] = (file_index_path, changes_num)

    files_stats = dict(sorted(files_stats.items(), key=lambda item: (-item[1][1], item[0])))

    out_path = os.path.join(output_base_dir_path, "index.html")
    _LOGGER.info("writing main page in file://%s", out_path)
    print_impact_page(files_stats, out_path)


def calculate_diff_file(input_base_file_path, base_config_path, output_base_dir_path):
    _LOGGER.info("handling file %s", input_base_file_path)

    input_filename = os.path.basename(input_base_file_path)
    out_file_path = os.path.join(output_base_dir_path, input_filename)

    with open(input_base_file_path, encoding="utf-8") as file_1:
        filebase_text = file_1.readlines()

    params_base_cfg_dict = read_params_space(base_config_path)
    # pprint.pprint(params_base_cfg_dict)
    ## convert to standard config dict
    params_base_cfg_dict = {key: subdict["value"] for key, subdict in params_base_cfg_dict.items()}

    changes = Changes("base", filebase_text)

    execute_uncrustify(input_base_file_path, base_config_path, out_file_path)

    with open(out_file_path, encoding="utf-8") as item_file:
        item_text = item_file.readlines()
    raw_diff = changes.calculate_diff(item_text)
    changed = changes.parse_diff(None, raw_diff)

    if not changed:
        # remove unused files
        os.remove(out_file_path)
        return None, None

    # write files diff to file
    raw_diff = "".join(raw_diff)
    diff_filename = name_to_diff_filename(input_filename)
    out_diff_path = os.path.join(output_base_dir_path, diff_filename)
    with open(out_diff_path, "w", encoding="utf-8") as out_file:
        out_file.write(raw_diff)

    out_path = os.path.join(output_base_dir_path, "index.html")
    print_diff_page(changes, out_path, input_filename)

    _LOGGER.info("output stored to: file://%s", out_path)
    total_changes = changes.count_changed_lines()
    return out_path, total_changes


def print_diff_page(changes: Changes, out_path, input_filename=None):
    top_content = None
    if input_filename is not None:
        top_content = f"""\
<div><b>Base file:</b> <a href="{input_filename}">{input_filename}</a></div>
"""

    total_changes = changes.count_changed_lines()
    bottom_content = f"""
<div class="section">Lines changed: {total_changes}</div>
"""

    # write general diff
    content = print_to_html(
        changes, label_converter=labels_to_links, top_content=top_content, bottom_content=bottom_content
    )
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)
