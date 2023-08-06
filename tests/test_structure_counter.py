#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import Dict

from neosca.structure_counter import Structure
from neosca.structure_counter import StructureCounter

from .base_tmpl import BaseTmpl


class TestStructure(BaseTmpl):
    def setUp(self):
        self.structures: Dict[str, Structure] = {}
        self.structures["W"] = Structure("W", "words")
        self.structures["S"] = Structure("S", "sentences")
        return super().setUp()


class TestStructureCounter(BaseTmpl):
    def setUp(self):
        self.selected_measures1 = {"VP", "T", "DC/C"}
        self.selected_measures2 = {"CP", "VP/T", "CN/C"}
        self.counter1 = StructureCounter(selected_measures=self.selected_measures1)
        self.counter2 = StructureCounter(selected_measures=self.selected_measures2)
        return super().setUp()

    def test_get_all_values(self):
        value_dict = self.counter1.get_all_values()
        self.assertTrue("Filename", value_dict.keys() - set(self.selected_measures1))

    def test_add(self):
        for s_name, value in (
            ("VP1", 5),
            ("VP2", 38),
            ("C1", 19),
            ("T1", 27),
            ("T2", 11),
            ("DC", 21),
        ):
            self.counter1.set_value(s_name, value)

        for s_name, value in (
            ("VP1", 4),
            ("C1", 3),
            ("T1", 41),
            ("T2", 8),
            ("CN1", 40),
            ("CN2", 16),
            ("CN3", 49),
            ("CP", 34),
        ):
            self.counter2.set_value(s_name, value)

        counter3 = self.counter1 + self.counter2
        expected_selected_measures3 = list(self.selected_measures1 | self.selected_measures2)
        self.assertEqual(len(counter3.selected_measures), len(expected_selected_measures3))
        for m in expected_selected_measures3:
            self.assertIn(m, counter3.selected_measures)

        value_dict = counter3.get_all_values()
        self.assertEqual({"Filename"}, value_dict.keys() - set(expected_selected_measures3))

        for s_name, value in (
            ("VP1", 9),
            ("VP2", 38),
            ("C1", 22),
            ("T1", 68),
            ("T2", 19),
            ("DC", 21),
            ("CN1", 40),
            ("CN2", 16),
            ("CN3", 49),
            ("CP", 34),
        ):
            self.assertEqual(counter3.get_value(s_name), value)
