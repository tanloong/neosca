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

    def test_parse_selected_measures(self):
        self.assertListEqual(
            ["VP", "T", "DC/C"], [s.name for s in self.counter1.structures_to_report]
        )
        self.assertListEqual(
            ["VP1", "VP2", "C1", "T1", "T2", "DC"],
            [s.name for s in self.counter1.structures_to_query],
        )
        self.assertListEqual(
            ["CP", "VP/T", "CN/C"], [s.name for s in self.counter2.structures_to_report]
        )
        self.assertListEqual(
            ["VP1", "C1", "T1", "T2", "CN1", "CN2", "CN3", "CP"],
            [s.name for s in self.counter2.structures_to_query],
        )

    def test_update_freqs(self):
        for s_name, freq in (
            ("VP1", 7),
            ("VP2", 1),
            ("C1", 9),
            ("C2", 1),
            ("T1", 11),
            ("T2", 1),
            ("CN1", 13),
            ("CN2", 1),
            ("CN3", 2),
        ):
            self.counter1.set_freq(s_name, freq)

        self.counter1.update_freqs()
        for s_name, freq in (
            ("VP", 8),
            ("C", 10),
            ("T", 12),
            ("CN", 16),
        ):
            self.assertEqual(self.counter1.structures[s_name].freq, freq)

    def test_compute_14_indices(self):
        for s_name, freq in (
            ("W", 1530),
            ("S", 54),
            ("VP1", 174),
            ("C1", 149),
            ("T", 83),
            ("DC", 61),
            ("CT", 52),
            ("CP", 26),
            ("CN", 181),
        ):
            self.counter1.set_freq(s_name, freq)

        self.counter1.compute_14_indicies()
        for s_name, freq in (
            ("W", 1530),
            ("S", 54),
            ("VP1", 174),
            ("C1", 149),
            ("T", 83),
            ("DC", 61),
            ("CT", 52),
            ("CP", 26),
            ("CN", 181),
            ("MLS", 28.3333),
            ("MLT", 18.4337),
            ("MLC", 10.2685),
            ("C/S", 2.7593),
            ("VP/T", 2.0964),
            ("C/T", 1.7952),
            ("DC/C", 0.4094),
            ("DC/T", 0.7349),
            ("T/S", 1.537),
            ("CT/T", 0.6265),
            ("CP/T", 0.3133),
            ("CP/C", 0.1745),
            ("CN/T", 2.1807),
            ("CN/C", 1.2148),
        ):
            self.assertEqual(self.counter1.structures[s_name].freq, freq)

    def test_get_freqs(self):
        freq_dict = self.counter1.get_all_freqs()
        self.assertTrue("Filename", freq_dict.keys() - set(self.selected_measures1))

    def test_add(self):
        for s_name, freq in (
            ("VP1", 5),
            ("VP2", 38),
            ("C1", 19),
            ("T1", 27),
            ("T2", 11),
            ("DC", 21),
        ):
            self.counter1.set_freq(s_name, freq)

        for s_name, freq in (
            ("VP1", 4),
            ("C1", 3),
            ("T1", 41),
            ("T2", 8),
            ("CN1", 40),
            ("CN2", 16),
            ("CN3", 49),
            ("CP", 34),
        ):
            self.counter2.set_freq(s_name, freq)

        counter3 = self.counter1 + self.counter2
        self.assertListEqual(
            ["VP", "T", "CP", "VP/T", "DC/C", "CN/C"],
            [s.name for s in counter3.structures_to_report],
        )
        self.assertListEqual(
            ["VP1", "VP2", "C1", "T1", "T2", "CN1", "CN2", "CN3", "DC", "CP"],
            [s.name for s in counter3.structures_to_query],
        )

        for s_name, freq in (
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
            self.assertEqual(counter3.structures[s_name].freq, freq)
