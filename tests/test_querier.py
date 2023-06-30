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
        counter.update_freqs()
        self.assertEqual(1, counter.structures["S"].freq)
        self.assertEqual(2, counter.structures["VP"].freq)
        self.assertEqual(1, counter.structures["C"].freq)
        self.assertEqual(1, counter.structures["T"].freq)
        self.assertEqual(0, counter.structures["DC"].freq)
        self.assertEqual(0, counter.structures["CT"].freq)
        self.assertEqual(0, counter.structures["CP"].freq)
        self.assertEqual(1, counter.structures["CN"].freq)
