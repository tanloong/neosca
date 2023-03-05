#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from neosca.querier import StanfordTregex
from neosca.structure_counter import StructureCounter

from .base_tmpl import BaseTmpl
from .base_tmpl import dir_stanford_tregex
from .base_tmpl import tree


class TestStanfordTregex(BaseTmpl):
    def setUp(self):
        self.counter = StructureCounter()
        self.tregex = StanfordTregex(dir_stanford_tregex)
        return super().setUp()

    def test_query(self):
        structures = self.tregex.query(self.counter, tree)
        structures.update_freqs()
        self.assertEqual(1, structures.S.freq)
        self.assertEqual(2, structures.VP.freq)
        self.assertEqual(1, structures.C.freq)
        self.assertEqual(1, structures.T.freq)
        self.assertEqual(0, structures.DC.freq)
        self.assertEqual(0, structures.CT.freq)
        self.assertEqual(0, structures.CP.freq)
        self.assertEqual(1, structures.CN.freq)
