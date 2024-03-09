#!/usr/bin/env python3

import csv
import glob
import logging
import os.path as os_path
from typing import List

from neosca.ns_lca.ns_lca_counter import Ns_LCA_Counter

from .base_tmpl import BaseTmpl


class TestLCACounter(BaseTmpl):
    def setUp(self):
        super().setUp()
        self.testdir_data_lempos = os_path.join(self.testdir_data, "lempos")

    def test_default_measures(self):
        c = Ns_LCA_Counter()
        self.assertEqual(len(c.DEFAULT_MEASURES), len(c.COUNT_ITEMS) * 2 + len(c.FREQ_ITEMS))
        for item in c.COUNT_ITEMS:
            for suffix in ("types", "tokens"):
                self.assertIn(f"{item}{suffix}", c.DEFAULT_MEASURES)
        for item in c.FREQ_ITEMS:
            self.assertIn(item, c.DEFAULT_MEASURES)

    def test_results(self):
        lempos_paths = glob.glob(f"{self.testdir_data_lempos}/*.lempos")
        assert len(lempos_paths) == 2

        with open(lempos_paths[0], encoding="utf-8") as f:
            lempos_tuples1 = [tuple(line.strip().split("_")) for line in f.readlines() if line.strip()]
            lempos_tuples1 = [(tup[0].lower(), tup[1]) for tup in lempos_tuples1]
        with open(lempos_paths[1], encoding="utf-8") as f:
            lempos_tuples2 = [tuple(line.strip().split("_")) for line in f.readlines() if line.strip()]
            lempos_tuples2 = [(tup[0].lower(), tup[1]) for tup in lempos_tuples2]

        c1 = Ns_LCA_Counter(tagset="ptb")
        c2 = Ns_LCA_Counter(tagset="ptb")

        c1.determine_all_values(lempos_tuples1)  # type: ignore
        c2.determine_all_values(lempos_tuples2)  # type: ignore

        with open(os_path.join(self.testdir_data_lempos, "lca_results.csv")) as f:
            csv_reader = csv.DictReader(f)
            expected_results: List[dict] = [row for row in csv_reader]

        # Compare results with original LCA implementation
        for counter, expected in zip((c1, c2), expected_results):
            for item in expected:
                if item in ("filename", "NDW-ER50", "NDW-ES50"):
                    continue
                logging.info(f"Comparing {item}...")
                self.assertEqual(round(counter.get_value(item), 2), float(expected[item].strip()))

        # Test combination
        c = Ns_LCA_Counter(tagset="ptb")
        c.determine_all_values(lempos_tuples=tuple(lempos_tuples1 + lempos_tuples2))  # type: ignore
        c_parent = c1 + c2

        for item in Ns_LCA_Counter.DEFAULT_MEASURES:
            if item in ("NDW-ER50", "NDW-ES50"):
                continue
            logging.info(f"Comparing {item}...")
            self.assertEqual(c.get_value(item), c_parent.get_value(item))
            self.assertEqual(c.get_matches(item), c_parent.get_matches(item))
