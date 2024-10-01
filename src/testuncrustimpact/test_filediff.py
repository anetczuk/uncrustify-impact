#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest

from uncrustimpact.filediff import LineModifiers, LineModifier
from uncrustimpact.filediff import NDiffChanges, UnifiedDiffChanges


class LineModifiersTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_add(self):
        modifiers = LineModifiers()

        modifiers.add_state("xxx", LineModifier.ADDED)
        modifiers.add_state("xxx", LineModifier.ADDED)
        modifiers.add_state("xxx", LineModifier.CHANGED)

        changes = modifiers.count_changes("xxx")
        self.assertEqual(2, changes)


class NDiffChangesTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_add_first(self):
        base_content = ["line1\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["new_line\n", "line1\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff()

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [("new.txt", "ADDED")], 0: [("new.txt", "SAME")]}, changes_dict)

    def test_add_middle(self):
        base_content = ["line1\n", "line2\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "new_line\n", "line2\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME"), ("new.txt", "ADDED")], 1: [("new.txt", "SAME")]}, changes_dict
        )

    def test_add_last(self):
        base_content = ["line1\n", "line2\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2\n", "new_line\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "SAME"), ("new.txt", "ADDED")]}, changes_dict
        )

    def test_changed_first_added(self):
        ## added content to first line
        base_content = ["line1\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1b\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_first_removed(self):
        ## removed content from first line
        base_content = ["line1\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_first_modified(self):
        ## removed content from first line
        base_content = ["line1\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line2\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_middle_added(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2b\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "CHANGED")], 2: [("new.txt", "SAME")]}, changes_dict
        )

    def test_changed_middle_change_add(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line\n", "2\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "CHANGED"), ("new.txt", "ADDED")],
                2: [("new.txt", "SAME")],
            },
            changes_dict,
        )

    def test_changed_middle_change_multiple(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n", "line4\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2b\n", "line3b\n", "line4\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "CHANGED")],
                2: [("new.txt", "CHANGED")],
                3: [("new.txt", "SAME")],
            },
            changes_dict,
        )

    # def test_changed_middle_change_remove(self):
    #     # added content in middle line
    #     base_content = ["line1\n", "line2a\n", "line2b\n", "line3a\n", "line3b\n", "line4\n"]
    #     changes = NDiffChanges("base.txt", base_content)
    #
    #     new_content = ["line1\n", "line21\n", "line22\n", "line4\n"]
    #     # changes.print_diff_raw(new_content)
    #     changes.add_diff("new.txt", new_content)
    #
    #     # changes.print_diff(False)
    #
    #     changes_dict = changes.to_dict_raw()
    #     self.assertDictEqual(
    #         {
    #             -1: [],
    #             0: [("new.txt", "SAME")],
    #             1: [("new.txt", "CHANGED")],
    #             2: [("new.txt", "CHANGED")],
    #             3: [("new.txt", "REMOVED")],
    #             4: [("new.txt", "REMOVED")],
    #             5: [("new.txt", "SAME")],
    #         },
    #         changes_dict,
    #     )

    def test_changed_last(self):
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2\n", "line3b\n"]
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "SAME")], 2: [("new.txt", "CHANGED")]}, changes_dict
        )

    def test_removed_first(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line2\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "REMOVED")], 1: [("new.txt", "SAME")], 2: [("new.txt", "SAME")]}, changes_dict
        )

    def test_removed_middle(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "REMOVED")], 2: [("new.txt", "SAME")]}, changes_dict
        )

    def test_removed_last(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = NDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2\n"]
        # changes.print_diff_raw(new_content)
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "SAME")], 2: [("new.txt", "REMOVED")]}, changes_dict
        )


class UnifiedDiffChangesTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_add_first(self):
        base_content = ["line1\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["new_line\n", "line1\n"]
        # ['--- ', '+++ ', '@@ -0,0 +1 @@', '+new_line\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff()

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [("new.txt", "ADDED")], 0: [("new.txt", "SAME")]}, changes_dict)

    def test_add_middle(self):
        base_content = ["line1\n", "line2\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "new_line\n", "line2\n"]
        # ['--- ', '+++ ', '@@ -1,0 +2 @@', '+new_line\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME"), ("new.txt", "ADDED")], 1: [("new.txt", "SAME")]}, changes_dict
        )

    def test_add_last(self):
        base_content = ["line1\n", "line2\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2\n", "new_line\n"]
        # ['--- ', '+++ ', '@@ -2,0 +3 @@', '+new_line\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "SAME"), ("new.txt", "ADDED")]}, changes_dict
        )

    def test_changed_first_added(self):
        ## added content to first line
        base_content = ["line1\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1b\n"]
        # ['--- ', '+++ ', '@@ -1 +1 @@', '-line1\n', '+line1b\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_first_removed(self):
        ## removed content from first line
        base_content = ["line1\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -1 +1 @@', '-line1\n', '+line\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_first_modified(self):
        ## removed content from first line
        base_content = ["line1\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line2\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -1 +1 @@', '-line1\n', '+line2\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual({-1: [], 0: [("new.txt", "CHANGED")]}, changes_dict)

    def test_changed_middle_added(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2b\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -2 +2 @@', '-line2\n', '+line2b\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "CHANGED")], 2: [("new.txt", "SAME")]}, changes_dict
        )

    def test_changed_middle_change_add(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line\n", "2\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -2 +2,2 @@', '-line2\n', '+line\n', '+2\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "CHANGED"), ("new.txt", "ADDED")],
                2: [("new.txt", "SAME")],
            },
            changes_dict,
        )

    def test_changed_middle_change_multiple(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n", "line4\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2b\n", "line3b\n", "line4\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -2,2 +2,2 @@', '-line2\n', '-line3\n', '+line2b\n', '+line3b\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "CHANGED")],
                2: [("new.txt", "CHANGED")],
                3: [("new.txt", "SAME")],
            },
            changes_dict,
        )

    def test_changed_middle_change_remove(self):
        # added content in middle line
        base_content = ["line1\n", "line2a\n", "line2b\n", "line3a\n", "line3b\n", "line4\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line21\n", "line22\n", "line4\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -2,4 +2,2 @@',
        #  '-line2a\n', '-line2b\n', '-line3a\n', '-line3b\n', '+line21\n', '+line22\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {
                -1: [],
                0: [("new.txt", "SAME")],
                1: [("new.txt", "CHANGED")],
                2: [("new.txt", "CHANGED")],
                3: [("new.txt", "REMOVED")],
                4: [("new.txt", "REMOVED")],
                5: [("new.txt", "SAME")],
            },
            changes_dict,
        )

    def test_changed_last(self):
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2\n", "line3b\n"]
        # ['--- ', '+++ ', '@@ -3 +3 @@', '-line3\n', '+line3b\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff_raw(new_content)
        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "SAME")], 2: [("new.txt", "CHANGED")]}, changes_dict
        )

    def test_removed_first(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line2\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -1 +0,0 @@', '-line1\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "REMOVED")], 1: [("new.txt", "SAME")], 2: [("new.txt", "SAME")]}, changes_dict
        )

    def test_removed_middle(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line3\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -2 +1,0 @@', '-line2\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "REMOVED")], 2: [("new.txt", "SAME")]}, changes_dict
        )

    def test_removed_last(self):
        # added content in middle line
        base_content = ["line1\n", "line2\n", "line3\n"]
        changes = UnifiedDiffChanges("base.txt", base_content)

        new_content = ["line1\n", "line2\n"]
        # changes.print_diff_raw(new_content)
        # ['--- ', '+++ ', '@@ -3 +2,0 @@', '-line3\n']
        changes.add_diff("new.txt", new_content)

        # changes.print_diff(False)

        changes_dict = changes.to_dict_raw()
        self.assertDictEqual(
            {-1: [], 0: [("new.txt", "SAME")], 1: [("new.txt", "SAME")], 2: [("new.txt", "REMOVED")]}, changes_dict
        )
