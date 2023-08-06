#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from neosca.querier import StanfordTregex
from neosca.structure_counter import StructureCounter

from .base_tmpl import BaseTmpl
from .base_tmpl import classpaths
from .base_tmpl import tree


class TestStanfordTregex(BaseTmpl):
    def setUp(self):
        self.counter = StructureCounter()
        self.tregex = StanfordTregex(classpaths=classpaths)
        return super().setUp()

    def test_query(self):
        counter = self.tregex.query(self.counter, tree)
        self.assertEqual(1, counter.get_value("S"))
        self.assertEqual(2, counter.get_value("VP"))
        self.assertEqual(1, counter.get_value("C"))
        self.assertEqual(1, counter.get_value("T"))
        self.assertEqual(0, counter.get_value("DC"))
        self.assertEqual(0, counter.get_value("CT"))
        self.assertEqual(0, counter.get_value("CP"))
        self.assertEqual(1, counter.get_value("CN"))
