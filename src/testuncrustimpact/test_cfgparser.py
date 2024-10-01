#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest

from uncrustimpact.cfgparser import read_doc_set, CfgLine


class CfgParserTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_read_doc_set_001(self):
        doc_string = "# Number of spaces before a trailing or embedded comment."
        allowed = read_doc_set(doc_string)
        self.assertEqual(None, allowed)

    def test_read_doc_set_002(self):
        doc_string = "# Virtual indent from the ':' for member initializers."
        allowed = read_doc_set(doc_string)
        self.assertEqual(None, allowed)

    def test_read_doc_set_valid(self):
        doc_string = """\
# How to use tabs when indenting code.
#
# 0: Spaces only
# 1: Indent with tabs to brace level, align with spaces (default)
# 2: Indent and align with tabs, using spaces when not on a tabstop
#
# Default: 1
"""
        allowed = read_doc_set(doc_string)
        self.assertEqual(["0", "1", "2"], allowed)


class CfgLineTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_raw_line_01(self):
        raw_line = "aa1=xxx"
        cfg_line = CfgLine(raw_line)

        self.assertEqual("", cfg_line.space0)
        self.assertEqual("aa1", cfg_line.name)
        self.assertEqual("", cfg_line.space1)
        self.assertEqual("", cfg_line.space2)
        self.assertEqual("xxx", cfg_line.value)
        self.assertEqual("", cfg_line.space3)
        self.assertEqual(None, cfg_line.comment)

        line_str = cfg_line.join()
        self.assertEqual(raw_line, line_str)

    def test_raw_line_02(self):
        raw_line = "aa1 = xxx"
        cfg_line = CfgLine(raw_line)

        self.assertEqual("", cfg_line.space0)
        self.assertEqual("aa1", cfg_line.name)
        self.assertEqual(" ", cfg_line.space1)
        self.assertEqual(" ", cfg_line.space2)
        self.assertEqual("xxx", cfg_line.value)
        self.assertEqual("", cfg_line.space3)
        self.assertEqual(None, cfg_line.comment)

        line_str = cfg_line.join()
        self.assertEqual(raw_line, line_str)

    def test_full_line(self):
        raw_line = " aa1  =   xxx    # qqq     "
        cfg_line = CfgLine(raw_line)

        self.assertEqual(" ", cfg_line.space0)
        self.assertEqual("aa1", cfg_line.name)
        self.assertEqual("  ", cfg_line.space1)
        self.assertEqual("   ", cfg_line.space2)
        self.assertEqual("xxx", cfg_line.value)
        self.assertEqual("    ", cfg_line.space3)
        self.assertEqual(" qqq     ", cfg_line.comment)

        line_str = cfg_line.join()
        self.assertEqual(raw_line, line_str)

    def test_comment_line(self):
        raw_line = "# qqq     "
        cfg_line = CfgLine(raw_line)

        self.assertEqual("", cfg_line.space0)
        self.assertEqual(None, cfg_line.name)
        self.assertEqual(None, cfg_line.space1)
        self.assertEqual(None, cfg_line.space2)
        self.assertEqual(None, cfg_line.value)
        self.assertEqual(None, cfg_line.space3)
        self.assertEqual(" qqq     ", cfg_line.comment)

        line_str = cfg_line.join()
        self.assertEqual(raw_line, line_str)

    def test_is_valid_empty(self):
        cfg_line = CfgLine("")
        self.assertEqual(False, cfg_line.is_valid())

    def test_is_valid_simple(self):
        cfg_line = CfgLine("aa1 = xxx")
        self.assertEqual(True, cfg_line.is_valid())

    def test_is_valid_comment(self):
        cfg_line = CfgLine("# qwe")
        self.assertEqual(False, cfg_line.is_valid())
