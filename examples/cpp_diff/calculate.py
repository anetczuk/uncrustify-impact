#!/usr/bin/env python3
#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#### append source root
sys.path.append(os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir, os.pardir, "src")))


# pylint: disable=C0413
from uncrustimpact.diff import Changes
from uncrustimpact.printhtml import print_to_html


def compare(filename_base, filename_list, outname):
    file1_path = os.path.join(SCRIPT_DIR, filename_base)

    with open(file1_path, encoding="utf-8") as file_1:
        filebase_text = file_1.readlines()

    changes = Changes(filename_base, filebase_text)

    for item in filename_list:
        item_path = os.path.join(SCRIPT_DIR, item)
        with open(item_path, encoding="utf-8") as item_file:
            item_text = item_file.readlines()
        changes.print_diff_raw(item_text)
        changes.add_diff(item, item_text)

    content = print_to_html(changes)

    print(content)

    out_path = os.path.join(SCRIPT_DIR, outname)

    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)

    changes.print_diff()


file1_name = "example.cpp"
file2_name = "example_changed.cpp"
file3_name = "example_changed2.cpp"

compare(file1_name, [file2_name], "diff1.html")
compare(file1_name, [file3_name], "diff2.html")
compare(file1_name, [file2_name, file3_name], "diff3.html")
