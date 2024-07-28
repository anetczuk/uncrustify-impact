# MIT License
#
# Copyright (c) 2020 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import unittest

from uncrustimpact.diff import Changes


class DiffTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_add_first(self):
        base_content = ["line1\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["new_line\n", "line1\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff()

        changes_dict = changes.to_dict_raw()
        self.assertEqual({-1: [("new.txt", "ADDED")], 0: [("new.txt", "SAME")]}, changes_dict)

    def test_add_middle(self):
        base_content = ["line1\n", "line2\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["line1\n", "new_line\n", "line2\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertEqual(
            {
                -1: [],
                0: [("new.txt", "SAME"), ("new.txt", "ADDED")],
                1: [("new.txt", "SAME")],
            },
            changes_dict,
        )

    def test_add_last(self):
        base_content = ["line1\n", "line2\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["line1\n", "line2\n", "new_line\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "SAME"), ("new.txt", "ADDED")],
            },
            changes_dict,
        )

    def test_changed_first_added(self):
        ## added content to first line
        base_content = ["line1\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["line1b\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_first_removed(self):
        ## removed content from first line
        base_content = ["line1\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["line\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_first_modified(self):
        ## removed content from first line
        base_content = ["line1\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["line2\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_middle_added(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["line1\n", "line2b\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "CHANGED")],
                2: [("new.txt", "SAME")],
            },
            changes_dict,
        )

    def test_changed_last(self):
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = Changes("base.txt", base_content)

        new_content = ["line1\n", "line2\n", "line3b\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "SAME")],
                2: [("new.txt", "CHANGED")],
            },
            changes_dict,
        )
