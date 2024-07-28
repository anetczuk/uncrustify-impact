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

from uncrustimpact.diff import Changes


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def print_to_html(changes: Changes) -> str:
    ret_content = """\
<html>
<head>
    <style>
        table pre {margin: 0;}
    </style>
</head>
<body>
"""

    changes_list = changes.to_list_raw()
    print(changes_list)

    ret_content += "<table>\n"

    # item: LineModifiers
    for index, line_content, modifier_state, files_list in changes_list:
        index_content = ""
        if index is not None:
            index_content = f"<pre>{index}:</pre>"

        if line_content:
            line_content = line_content.rstrip("\r\n")
            line_content = html.escape(line_content)
            line_content = f"<pre>{line_content}</pre>"

        if modifier_state:
            if modifier_state == "added":
                modifier_state = "a"
            elif modifier_state == "modified":
                modifier_state = "m"
            modifier_state = f"{modifier_state}: " + " ".join(files_list)
        else:
            modifier_state = ""

        ret_content += f"<tr><td>{index_content}</td> <td>{line_content}</td> <td>{modifier_state}</td></tr>\n"

    ret_content += "</table>\n"

    ret_content += "</body></html>\n"
    return ret_content
