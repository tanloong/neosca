#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from .base_tmpl import BaseTmpl
from .base_tmpl import text
from .base_tmpl import tree as tree_expected
from .base_tmpl import dir_stanford_parser
from neosca.parser import StanfordParser


class TestStanfordParser(BaseTmpl):
    def setUp(self):
        self.parser = StanfordParser(dir_stanford_parser)
        return super().setUp()

    def test_parse(self):
        tree = self.parser.parse(text).strip()
        self.assertEqual(tree_expected, tree)

    def test_is_long(self):
        max_length = 100
        length_1 = 99
        length_2 = 100
        length_3 = 101
        self.assertFalse(self.parser._is_long(length_1, max_length))
        self.assertFalse(self.parser._is_long(length_2, max_length))
        self.assertTrue(self.parser._is_long(length_3, max_length))
        self.assertFalse(self.parser._is_long(length_3))
