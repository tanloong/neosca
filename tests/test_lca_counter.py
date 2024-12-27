#!/usr/bin/env python3

import csv
import glob
import logging
import os.path as os_path
import random
import string

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

    def test_msttr(self):
        # fake words
        words = tuple("".join(random.choices(string.ascii_letters, k=4)) for _ in range(1000))
        msttr = Ns_LCA_Counter.get_msttr(words, section_size=50)
        self.assertGreater(msttr, 0)
        self.assertLessEqual(msttr, 1)

        msttr = Ns_LCA_Counter.get_msttr([], section_size=50)
        self.assertEqual(msttr, 0)

        msttr = Ns_LCA_Counter.get_msttr(words, section_size=len(words))
        self.assertEqual(msttr, len(set(words)) / len(words))
        msttr = Ns_LCA_Counter.get_msttr(words, section_size=len(words) + 1)
        self.assertEqual(msttr, len(set(words)) / len(words))

        self.assertRaises(ValueError, Ns_LCA_Counter.get_msttr, words, section_size=0)
        self.assertRaises(ValueError, Ns_LCA_Counter.get_msttr, words, section_size=-1)

    def test_mattr(self):
        # fake words
        words = tuple("".join(random.choices(string.ascii_letters, k=4)) for _ in range(1000))
        mattr = Ns_LCA_Counter.get_mattr(words, window_size=50)
        self.assertGreater(mattr, 0)
        self.assertLessEqual(mattr, 1)

        mattr = Ns_LCA_Counter.get_mattr([], window_size=50)
        self.assertEqual(mattr, 0)

        mattr = Ns_LCA_Counter.get_mattr(words, window_size=len(words))
        self.assertEqual(mattr, len(set(words)) / len(words))
        mattr = Ns_LCA_Counter.get_mattr(words, window_size=len(words) + 1)
        self.assertEqual(mattr, len(set(words)) / len(words))

        self.assertRaises(ValueError, Ns_LCA_Counter.get_mattr, words, window_size=0)
        self.assertRaises(ValueError, Ns_LCA_Counter.get_mattr, words, window_size=-1)

    def test_results(self):
        lempos_paths = glob.glob(f"{self.testdir_data_lempos}/*.lempos")
        assert len(lempos_paths) == 2

        counters = []
        lempos_tuples_list = []
        for lempos_path in lempos_paths:
            with open(lempos_path, encoding="utf-8") as f:
                lempos_tuples = [tuple(line.strip().split("_")) for line in f.readlines() if line.strip()]
                lempos_tuples = [(tup[0].lower(), tup[1]) for tup in lempos_tuples]
                c = Ns_LCA_Counter(file_path=lempos_path, tagset="ptb")
                c.determine_all_values(lempos_tuples)  # type: ignore
                counters.append(c)
                lempos_tuples_list.append(lempos_tuples)

        with open(os_path.join(self.testdir_data_lempos, "lca_results.csv")) as f:
            csv_reader = csv.DictReader(f)
            expected_results: list[dict] = [row for row in csv_reader]
        assert len(expected_results) == len(counters)

        # Compare results with original LCA implementation
        for counter in counters:
            for expected in expected_results:
                if os_path.basename(counter.file_path) == expected["filename"]:
                    for item in expected:
                        if item in ("filename", "NDW-ER50", "NDW-ES50"):
                            continue
                        logging.info(f"Comparing {item}...")
                        self.assertEqual(round(counter.get_value(item), 2), float(expected[item].strip()))
                    break
            else:
                assert False, "Found no corresponding expected result"

        # Test combination
        c = Ns_LCA_Counter(tagset="ptb")
        c.determine_all_values(
            lempos_tuples=tuple(t for lempos_tuples in lempos_tuples_list for t in lempos_tuples)  # type: ignore
        )
        c_parent = Ns_LCA_Counter()
        for counter in counters:
            c_parent = c_parent + counter

        for item in Ns_LCA_Counter.DEFAULT_MEASURES:
            if item in ("NDW-ER50", "NDW-ES50"):
                continue
            logging.info(f"Comparing {item}...")
            self.assertEqual(c.get_value(item), c_parent.get_value(item))
            self.assertEqual(c.get_matches(item), c_parent.get_matches(item))
