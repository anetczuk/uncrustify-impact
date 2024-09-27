#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import html

from uncrustimpact.filediff import Changes, LineModifier
from uncrustimpact.cfgparser import ParamType


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def print_to_html(changes: Changes, label_converter=None, top_content=None, bottom_content=None) -> str:
    ret_content = """\
<html>
<head>
    <style>
        table { padding: 6px; }
        table pre { margin: 0; }

        .section { margin-top: 24px; font-weight: bold; }

        .codediff { background-color: #abb2b9; }
        .codediff .added { background-color: #eaecee; }
        .codediff .changed { background-color: #d5d8dc; }
        .codediff .removed { background-color: #808b96; }

        .codediff .colnum { padding-right: 12; }
        .codediff .colmod { padding-left: 12; }
    </style>
</head>
<body>
"""
    if top_content is not None:
        ret_content += top_content
    ret_content += """\
<div class="section">File impact:</div>
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
            modifier_label = " | ".join(labels_list)

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


def print_impact_page(files_stats_dict, output_path):
    output_dir = os.path.dirname(output_path)
    output_dir_len = len(output_dir)
    if output_dir_len > 0:
        output_dir_len += 1  # include slash

    content = """\
<html>
<head>
</head>
<body>
    <table>
        <tr style="text-align: left;"> <th>File:</th>               <th>Number of changes:</th>  </tr>
"""

    total_changes = 0
    for file_path, changes_data in files_stats_dict.items():
        target_path = changes_data[0]
        if target_path.startswith(output_dir):
            target_path = target_path[output_dir_len:]
        changes_num = changes_data[1]
        content += f"""\
        <tr> \
<td><a href="{target_path}">{file_path}</a></td> \
<td>{changes_num}</td> \
</tr>
"""
        total_changes += changes_num

    content += f"""\
    </table>
<div style="margin-top: 12px"><b>Total changes:</b><span style="margin-left: 12px">{total_changes}</span></div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)


def print_impactparam_page(param_name, param_data_list, param_prev_value, param_def, changed_lines, output_dir):
    value_set_text = ""
    if param_def["type"] == ParamType.SET:
        allowed_list = sorted(param_def["allowed"])
        allowed_list = " ".join(allowed_list)
        value_set_text = f"""<tr> <td>Allowed values:</td>      <td>{allowed_list}</td> </tr>"""

    param_doc_text = ""
    if "doc" in param_def:
        param_doc_text = f"""<tr> <td>Doc:</td>            <td><pre>{param_def["doc"]}</pre></td>   </tr>"""

    content = f"""\
<html>
<head>
</head>
<body>
    <table>
        <tr> <td>Parameter:</td>      <td><b>{param_name}</b></td>  </tr>
        <tr> <td>Changed lines:</td>  <td>{changed_lines}</td>      </tr>
        <tr> <td>Type:</td>           <td>{param_def["type"]}</td>  </tr>
        {value_set_text}
        <tr> <td>Default value:</td>  <td>{param_def["value"]}</td> </tr>
        <tr> <td>Prev value:</td>     <td>{param_prev_value}</td>   </tr>
        {param_doc_text}
    </table>
"""

    if param_data_list:
        content += """\
    <table>
        <tr>
            <th>New value:</th>
        </tr>
"""

        for param_data in param_data_list:
            param_val = param_data[0]
            config_output = param_data[1]
            file_output = param_data[2]
            diff_output = param_data[3]
            content += f"""\
        <tr> \
<td>{param_val}</td> \
<td><a href="{file_output}">output</a></td> \
<td><a href="{diff_output}">diff</a></td> \
<td><a href="{config_output}">config</a></td> \
</tr>
"""
        content += """\
    </table>
"""

    content += """\
</body>
</html>
"""
    out_path = os.path.join(output_dir, f"{param_name}.html")
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)


def generate_params_stats(params_stats_dict, label_to_link=None):
    ret_content = """\
<div class="section">Parameters impact:</div>
<table>
    <tr style="text-align: left;"> <th>Parameter:</th> <th>Lines changed:</th> </tr>
"""

    for param_name, param_count in params_stats_dict.items():
        label = param_name
        if label_to_link:
            label = label_to_link(param_name)
        ret_content += f"""    \
<tr>\
<td>{label}</td> \
<td>{param_count}</td> \
</tr>
"""

    ret_content += "</table>\n"

    impact_list = sorted([par_name for par_name, par_impact in params_stats_dict.items() if par_impact > 0])
    zero_list = sorted([par_name for par_name, par_impact in params_stats_dict.items() if par_impact == 0])

    impact_list = " ".join(impact_list)
    zero_list = " ".join(zero_list)

    ret_content += f"""\

    <div class="section">Parameters with impact:</div>
    <div>{impact_list}</div>

    <div class="section">Parameters without impact:</div>
    <div>{zero_list}</div>
"""

    return ret_content


# ===============================================================


def print_fit_page(best_cfg_path, best_fit, output_path):
    output_dir = os.path.dirname(output_path)
    output_dir_len = len(output_dir)
    if output_dir_len > 0:
        output_dir_len += 1  # include slash

    content = f"""\
<html>
<head>
</head>
<body>
    <div><b>Best config:</b> <a href="{best_cfg_path}">config</a></div>

    <table style="margin-top: 12px">
        <tr style="text-align: left;">  <th>Parameter with impact:</th> <th>Best value:</th> <th>Smallest num of changes:</th>  </tr>
"""

    for key, item in best_fit.items():
        ## we want to show all parameters, those with 0 changes too
        is_changed = item[1]
        if is_changed is False:
            continue
        param_page_path = item[3]
        content += f"""\
        <tr> \
<td><a href="{param_page_path}">{key}</a></td> \
<td>{item[0]}</td> \
<td>{item[2]}</td> \
</tr>
"""

    content += """\
    </table>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)


def print_fitparam_page(param_item, best_value, param_results, output_file_path):
    param_name = param_item[0]
    param_def = param_item[1]
    cfg_value = param_item[3]

    value_set_text = ""
    if param_def["type"] == ParamType.SET:
        allowed_list = sorted(param_def["allowed"])
        allowed_list = " ".join(allowed_list)
        value_set_text = f"""<tr> <td>Allowed values:</td>      <td>{allowed_list}</td> </tr>"""

    param_doc_text = ""
    if "doc" in param_def:
        param_doc_text = f"""<tr> <td>Doc:</td>            <td><pre>{param_def["doc"]}</pre></td>   </tr>"""

    content = f"""\
<html>
<head>
</head>
<body>
    <table>
        <tr> <td>Parameter:</td>      <td><b>{param_name}</b></td>  </tr>
        <tr> <td>Type:</td>           <td>{param_def["type"]}</td>  </tr>
        {value_set_text}
        <tr> <td>Default value:</td>  <td>{param_def["value"]}</td> </tr>
        <tr> <td>Config value:</td>   <td>{cfg_value}</td> </tr>
        <tr> <td>Best value:</td>     <td>{best_value}</td> </tr>
        {param_doc_text}
    </table>
"""

    if param_results:
        content += """\
    <table>
        <tr>
            <th>New value:</th>
            <th>Changed lines:</th>
        </tr>
"""

        for param_changes_counter, param_data in param_results:
            param_val = param_data[0]
            param_dir = param_val
            # param_dir = param_data[1]
            change_link = f"""<a href="{param_dir}/index.html">{param_changes_counter}</a>"""

            diff_link = f"""{param_dir}/diff.txt"""
            content += f"""\
        <tr> \
<td>{param_val}</td> \
<td>{change_link}</td> \
<td><a href="{diff_link}">diff</a></td> \
</tr>
"""
        content += """\
    </table>
"""

    content += """\
</body>
</html>
"""
    with open(output_file_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)
