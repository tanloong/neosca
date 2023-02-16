#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from .base_tmpl import BaseTmpl
from .base_tmpl import ifile_text
from .base_tmpl import tree as tree_expected
from .base_tmpl import dir_stanford_parser
from neosca.parser import StanfordParser
class TestStanfordParser(BaseTmpl):
    def setUp(self):
        self.parser = StanfordParser(dir_stanford_parser)
        return super().setUp()
    def test_parse(self):
        tree = self.parser.parse(ifile_text).strip()
        self.assertEqual(tree_expected, tree)
