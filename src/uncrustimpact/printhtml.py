#!/usr/bin/env python3
#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import html

from uncrustimpact.diff import Changes, LineModifier


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def print_to_html(changes: Changes, label_converter=None, bottom_content=None) -> str:
    ret_content = """\
<html>
<head>
    <style>
        table { padding: 6px; }
        table pre { margin: 0; }

        .codediff { background-color: #abb2b9; }
        .codediff .added { background-color: #eaecee; }
        .codediff .changed { background-color: #d5d8dc; }
        .codediff .removed { background-color: #808b96; }

        .codediff .colnum { padding-right: 12; }
        .codediff .colmod { padding-left: 12; }
    </style>
</head>
<body>
<div>File impact:</div>
"""

    changes_list = changes.to_list_raw(removed_as_changed=True, do_not_repeat=True)
    # import pprint
    # print("raw list:")
    # pprint.pprint(changes_list, indent=4)

    ret_content += """<table cellspacing="0" class="codediff">\n"""

    prev_line = -1
    # item: LineModifiers
    for line_num, line_content, modifier_state, labels_list in changes_list:
        index_content = ""
        if line_num is not None:
            index_content = f"<pre>{line_num}:</pre>"

        if line_content:
            line_content = line_content.rstrip("\r\n")
            line_content = html.escape(line_content)
            line_content = f"<pre>{line_content}</pre>"

        modifier_label = ""
        if modifier_state == LineModifier.SAME:
            modifier_label = ""
        elif modifier_state == LineModifier.ADDED:
            modifier_label = "a"
        elif modifier_state == LineModifier.CHANGED:
            modifier_label = "m"
        elif modifier_state == LineModifier.REMOVED:
            modifier_label = "r"
        else:
            raise RuntimeError(f"invalid state: {modifier_state}")

        modifier_label = ""
        if label_converter:
            labels_list = label_converter(labels_list)
        if labels_list:
            modifier_label = " ".join(labels_list)

        if prev_line == line_num:
            index_content = ""
            line_content = ""

        row_class = modifier_state.name.lower()

        ret_content += f"""<tr class="line {row_class}">\
<td class="colnum">{index_content}</td> \
<td class="colcode">{line_content}</td> \
<td class="colmod">{modifier_label}</td>\
</tr>\n"""

        prev_line = line_num

    ret_content += "</table>\n"

    if bottom_content:
        ret_content += f"{bottom_content}\n"

    ret_content += "</body></html>\n"
    return ret_content


def print_param_page(param_name, param_prev_value, param_value, diff_filename, output_dir):
    content = f"""\
<html>
<head>
</head>
<body>
    <div>Parameter: {param_name}</div>
    <div>Prev value: {param_prev_value}</div>
    <div>New value: {param_value}</div>
    <div><a href="{param_name}.txt">output</a></div>
    <div><a href="{diff_filename}">diff</a></div>
    <div><a href="{param_name}.cfg">config</a></div>
</body>
</html>
"""
    out_path = os.path.join(output_dir, f"{param_name}.html")
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)


def generate_params_stats(params_stats_dict, label_to_link=None):
    ret_content = """<div style="margin-top: 24px;">Parameters impact:</div>"""
    ret_content += """<table>\n"""

    for param_name, param_count in params_stats_dict.items():
        label = param_name
        if label_to_link:
            label = label_to_link(param_name)
        ret_content += f"""<tr>\
<td>{label}</td> \
<td>{param_count}</td> \
</tr>\n"""

    ret_content += "</table>\n"
    return ret_content
