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

from uncrustimpact.cfgparser import read_doc_set


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
