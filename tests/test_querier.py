#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from neosca.scaexceptions import (
    RecursiveDefinitionError,
    StructureNotFoundError,
)
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

    def test_set_value(self):
        kwargs_recursive_defs = {
            "ifile": "",
            "user_structure_defs": [
                # recursion 1
                {"name": "A", "value_source": "A"},
                # recursion 2
                {"name": "B", "value_source": "C + B"},
                {"name": "C", "tregex_pattern": "C !< __"},
                # recursion 3
                {"name": "D", "value_source": "E"},
                {"name": "E", "value_source": "F"},
                {"name": "F", "value_source": "D"},
                # non-existing dependant
                {"name": "G", "value_source": "NULL"},
            ],
        }
        counter = StructureCounter(**kwargs_recursive_defs)
        self.assertRaises(RecursiveDefinitionError, self.tregex.set_value, counter, "A", tree)
        self.assertRaises(RecursiveDefinitionError, self.tregex.set_value, counter, "B", tree)
        self.assertRaises(RecursiveDefinitionError, self.tregex.set_value, counter, "D", tree)

        self.assertRaises(StructureNotFoundError, self.tregex.set_value, counter, "G", tree)

    # def test_query(self):
    #     counter = self.tregex.query(self.counter, tree)
    #     self.assertEqual(1, counter.get_value("S"))
    #     self.assertEqual(2, counter.get_value("VP"))
    #     self.assertEqual(1, counter.get_value("C"))
    #     self.assertEqual(1, counter.get_value("T"))
    #     self.assertEqual(0, counter.get_value("DC"))
    #     self.assertEqual(0, counter.get_value("CT"))
    #     self.assertEqual(0, counter.get_value("CP"))
    #     self.assertEqual(1, counter.get_value("CN"))
