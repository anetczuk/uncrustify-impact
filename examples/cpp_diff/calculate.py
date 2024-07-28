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


def compare(filename1, filename2, outname):
    file1_path = os.path.join(SCRIPT_DIR, filename1)
    file2_path = os.path.join(SCRIPT_DIR, filename2)

    with open(file1_path, encoding="utf-8") as file_1:
        file1_text = file_1.readlines()

    with open(file2_path, encoding="utf-8") as file_2:
        file2_text = file_2.readlines()

    changes = Changes(filename1, file1_text)

    changes.add_diff(filename2, file2_text)

    changes.print_diff_raw(file2_text)

    content = print_to_html(changes)

    print(content)

    out_path = os.path.join(SCRIPT_DIR, outname)

    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)

    changes.print_diff()


file1_name = "example.cpp"
file2_name = "example_changed.cpp"
file3_name = "example_changed2.cpp"

compare(file1_name, file2_name, "diff1.html")
compare(file1_name, file3_name, "diff2.html")
