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
        self.counter1.structures["VP1"].freq, self.counter1.structures["VP2"].freq = 7, 1
        self.counter1.structures["C1"].freq, self.counter1.structures["C2"].freq = 9, 1
        self.counter1.structures["T1"].freq, self.counter1.structures["T2"].freq = 11, 1
        self.counter1.structures["CN1"].freq, self.counter1.structures["CN2"].freq, self.counter1.structures["CN3"].freq = 13, 1, 2

        self.counter1.update_freqs()
        self.assertEqual(8, self.counter1.structures["VP"].freq)
        self.assertEqual(10, self.counter1.structures["C"].freq)
        self.assertEqual(12, self.counter1.structures["T"].freq)
        self.assertEqual(16, self.counter1.structures["CN"].freq)

    def test_compute_14_indices(self):
        (
            self.counter1.structures["W"].freq,
            self.counter1.structures["S"].freq,
            self.counter1.structures["VP1"].freq,
            self.counter1.structures["C1"].freq,
            self.counter1.structures["T"].freq,
            self.counter1.structures["DC"].freq,
            self.counter1.structures["CT"].freq,
            self.counter1.structures["CP"].freq,
            self.counter1.structures["CN"].freq,
        ) = (1530, 54, 174, 149, 83, 61, 52, 26, 181)
        self.counter1.compute_14_indicies()
        self.assertEqual(1530, self.counter1.structures["W"].freq)
        self.assertEqual(54, self.counter1.structures["S"].freq)
        self.assertEqual(174, self.counter1.structures["VP1"].freq)
        self.assertEqual(149, self.counter1.structures["C1"].freq)
        self.assertEqual(83, self.counter1.structures["T"].freq)
        self.assertEqual(61, self.counter1.structures["DC"].freq)
        self.assertEqual(52, self.counter1.structures["CT"].freq)
        self.assertEqual(26, self.counter1.structures["CP"].freq)
        self.assertEqual(181, self.counter1.structures["CN"].freq)
        self.assertEqual(28.3333, self.counter1.structures["MLS"].freq)
        self.assertEqual(18.4337, self.counter1.structures["MLT"].freq)
        self.assertEqual(10.2685, self.counter1.structures["MLC"].freq)
        self.assertEqual(2.7593, self.counter1.structures["C/S"].freq)
        self.assertEqual(2.0964, self.counter1.structures["VP/T"].freq)
        self.assertEqual(1.7952, self.counter1.structures["C/T"].freq)
        self.assertEqual(0.4094, self.counter1.structures["DC/C"].freq)
        self.assertEqual(0.7349, self.counter1.structures["DC/T"].freq)
        self.assertEqual(1.537, self.counter1.structures["T/S"].freq)
        self.assertEqual(0.6265, self.counter1.structures["CT/T"].freq)
        self.assertEqual(0.3133, self.counter1.structures["CP/T"].freq)
        self.assertEqual(0.1745, self.counter1.structures["CP/C"].freq)
        self.assertEqual(2.1807, self.counter1.structures["CN/T"].freq)
        self.assertEqual(1.2148, self.counter1.structures["CN/C"].freq)

    def test_get_freqs(self):
        freq_dict = self.counter1.get_freqs()
        self.assertTrue("Filename", freq_dict.keys() - set(self.selected_measures1))

    def test_add(self):
        (
            self.counter1.structures["VP1"].freq,
            self.counter1.structures["VP2"].freq,
            self.counter1.structures["C1"].freq,
            self.counter1.structures["T1"].freq,
            self.counter1.structures["T2"].freq,
            self.counter1.structures["DC"].freq,
        ) = (5, 38, 19, 27, 11, 21)
        (
            self.counter2.structures["VP1"].freq,
            self.counter2.structures["C1"].freq,
            self.counter2.structures["T1"].freq,
            self.counter2.structures["T2"].freq,
            self.counter2.structures["CN1"].freq,
            self.counter2.structures["CN2"].freq,
            self.counter2.structures["CN3"].freq,
            self.counter2.structures["CP"].freq,
        ) = (4, 3, 41, 8, 40, 16, 49, 34)
        counter3 = self.counter1 + self.counter2
        self.assertListEqual(
            ["VP", "T", "CP", "VP/T", "DC/C", "CN/C"],
            [s.name for s in counter3.structures_to_report],
        )
        self.assertListEqual(
            ["VP1", "VP2", "C1", "T1", "T2", "CN1", "CN2", "CN3", "DC", "CP"],
            [s.name for s in counter3.structures_to_query],
        )
        self.assertEqual(9, counter3.structures["VP1"].freq)
        self.assertEqual(38, counter3.structures["VP2"].freq)
        self.assertEqual(22, counter3.structures["C1"].freq)
        self.assertEqual(68, counter3.structures["T1"].freq)
        self.assertEqual(19, counter3.structures["T2"].freq)
        self.assertEqual(21, counter3.structures["DC"].freq)
        self.assertEqual(40, counter3.structures["CN1"].freq)
        self.assertEqual(16, counter3.structures["CN2"].freq)
        self.assertEqual(49, counter3.structures["CN3"].freq)
        self.assertEqual(34, counter3.structures["CP"].freq)
