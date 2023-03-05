#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from .base_tmpl import BaseTmpl
from neosca.structure_counter import Structure
from neosca.structure_counter import StructureCounter


class TestStructure(BaseTmpl):
    def setUp(self):
        self.W = Structure("W", "words")
        self.S = Structure("S", "sentences")
        return super().setUp()

    def test_div(self):
        self.W.freq = 25
        self.S.freq = 2
        self.assertEqual(12.5, self.W / self.S)
        self.S.freq = 0
        self.assertEqual(0, self.W / self.S)


class TestStructureCounter(BaseTmpl):
    def setUp(self):
        self.selected_measures = {"VP", "T", "DC_C"}
        self.counter = StructureCounter(selected_measures=self.selected_measures)
        return super().setUp()

    def test_update_freqs(self):
        self.counter.VP1.freq, self.counter.VP2.freq = 7, 1
        self.counter.C1.freq, self.counter.C2.freq = 9, 1
        self.counter.T1.freq, self.counter.T2.freq = 11, 1
        self.counter.CN1.freq, self.counter.CN2.freq, self.counter.CN3.freq = 13, 1, 2

        self.counter.update_freqs()
        self.assertEqual(8, self.counter.VP.freq)
        self.assertEqual(10, self.counter.C.freq)
        self.assertEqual(12, self.counter.T.freq)
        self.assertEqual(16, self.counter.CN.freq)

    def test_compute_14_indices(self):
        (
            self.counter.W.freq,
            self.counter.S.freq,
            self.counter.VP1.freq,
            self.counter.C1.freq,
            self.counter.T.freq,
            self.counter.DC.freq,
            self.counter.CT.freq,
            self.counter.CP.freq,
            self.counter.CN.freq,
        ) = (1530, 54, 174, 149, 83, 61, 52, 26, 181)
        self.counter.compute_14_indicies()
        self.assertEqual(1530, self.counter.W.freq)
        self.assertEqual(54, self.counter.S.freq)
        self.assertEqual(174, self.counter.VP1.freq)
        self.assertEqual(149, self.counter.C1.freq)
        self.assertEqual(83, self.counter.T.freq)
        self.assertEqual(61, self.counter.DC.freq)
        self.assertEqual(52, self.counter.CT.freq)
        self.assertEqual(26, self.counter.CP.freq)
        self.assertEqual(181, self.counter.CN.freq)
        self.assertEqual(28.3333, self.counter.MLS.freq)
        self.assertEqual(18.4337, self.counter.MLT.freq)
        self.assertEqual(10.2685, self.counter.MLC.freq)
        self.assertEqual(2.7593, self.counter.C_S.freq)
        self.assertEqual(2.0964, self.counter.VP_T.freq)
        self.assertEqual(1.7952, self.counter.C_T.freq)
        self.assertEqual(0.4094, self.counter.DC_C.freq)
        self.assertEqual(0.7349, self.counter.DC_T.freq)
        self.assertEqual(1.537, self.counter.T_S.freq)
        self.assertEqual(0.6265, self.counter.CT_T.freq)
        self.assertEqual(0.3133, self.counter.CP_T.freq)
        self.assertEqual(0.1745, self.counter.CP_C.freq)
        self.assertEqual(2.1807, self.counter.CN_T.freq)
        self.assertEqual(1.2148, self.counter.CN_C.freq)

    def test_get_freqs(self):
        freq_dict = self.counter.get_freqs()
        self.assertTrue("Filename", freq_dict.keys() - set(self.selected_measures))
