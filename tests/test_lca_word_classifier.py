#!/usr/bin/env python3

from neosca import DATA_DIR
from neosca.ns_io import Ns_IO
from neosca.ns_lca.ns_lca_counter import Ns_LCA_Counter
from neosca.ns_lca.word_classifiers import Ns_PTB_Word_Classifier, Ns_UD_Word_Classifier

from .base_tmpl import BaseTmpl


class TestWordClassifier(BaseTmpl):
    def setUp(self):
        super().setUp()
        word_data = Ns_IO.load_pickle_lzma(DATA_DIR / Ns_LCA_Counter.WORDLIST_DATAFILE_MAP["bnc"])
        self.ptb = Ns_PTB_Word_Classifier(word_data=word_data)
        self.ud = Ns_UD_Word_Classifier(word_data=word_data)

    def test_misc(self):
        ud_tests = (
            (" ", "postag", True),
            ("lemma", "PUNCT", True),
            ("lemma", "SYM", True),
            ("lemma", "SPACE", True),
            ("'", "postag", True),
            ("'", "X", True),
        )
        ptb_tests = (
            (" ", "postag", True),
            ("lemma", ",", True),
            ("lemma", "SENT", True),
            ("lemma", "SYM", True),
            ("lemma", "HYPH", True),
            ("'", "postag", True),
        )

        for lemma, pos, res in ud_tests:
            self.assertEqual(self.ud.is_("misc", lemma, pos), res)
        for lemma, pos, res in ptb_tests:
            self.assertEqual(self.ptb.is_("misc", lemma, pos), res)

    def test_noun(self):
        ptb_tests = (
            ("lemma", "NN", True),
            ("lemma", "NNS", True),
            ("lemma", "NNP", True),
            ("lemma", "NNPS", True),
        )
        ud_tests = (
            ("lemma", "NOUN", True),
            ("lemma", "PROPN", True),
        )

        for lemma, pos, res in ptb_tests:
            self.assertEqual(self.ptb.is_("noun", lemma, pos), res)
        for lemma, pos, res in ud_tests:
            self.assertEqual(self.ud.is_("noun", lemma, pos), res)

    def test_verb(self):
        ud_tests = (("lemma", "VERB", True),)
        ptb_tests = (
            ("lemma", "VB", True),
            ("lemma", "VBD", True),
            ("lemma", "VBG", True),
            ("lemma", "VBN", True),
            ("lemma", "VBP", True),
            ("lemma", "VBZ", True),
        )

        for lemma, pos, res in ptb_tests:
            self.assertEqual(self.ptb.is_("verb", lemma, pos), res)
        for lemma, pos, res in ud_tests:
            self.assertEqual(self.ud.is_("verb", lemma, pos), res)

    def test_adj(self):
        ptb_tests = (
            ("lemma", "JJ", True),
            ("lemma", "JJR", True),
            ("lemma", "JJS", True),
        )
        ud_tests = (("lemma", "ADJ", True),)

        for lemma, pos, res in ptb_tests:
            self.assertEqual(self.ptb.is_("adj", lemma, pos), res)
        for lemma, pos, res in ud_tests:
            self.assertEqual(self.ud.is_("adj", lemma, pos), res)

    def test_adv(self):
        ptb_adv = next(iter(self.ptb.adj_dict.keys()))
        ptb_tests = (
            (ptb_adv, "not-startswith-R", False),
            (ptb_adv, "RB", True),
            (ptb_adv, "RBR", True),
            (ptb_adv, "RBS", True),
            (ptb_adv, "RP", True),
            (f"{ptb_adv}ly", "RB", True),
            (f"{ptb_adv}ly", "RBR", True),
            (f"{ptb_adv}ly", "RBS", True),
            (f"{ptb_adv}ly", "RP", True),
        )
        ud_adv = next(iter(self.ud.adj_dict.keys()))
        ud_tests = (
            (ud_adv, "not-ADV", False),
            (ud_adv, "ADV", True),
            (f"{ud_adv}ly", "ADV", True),
        )

        for lemma, pos, res in ptb_tests:
            self.assertEqual(self.ptb.is_("adv", lemma, pos), res)
        for lemma, pos, res in ud_tests:
            self.assertEqual(self.ud.is_("adv", lemma, pos), res)

    def test_sword(self):
        ptb_threshold = self.ptb.easy_word_threshold
        ptb_tests = (
            (self.ptb.word_ranks[ptb_threshold], "postag", True),
            (self.ptb.word_ranks[ptb_threshold], "CD", False),
            (self.ptb.word_ranks[ptb_threshold - 1], "postag", False),
        )
        ud_threshold = self.ud.easy_word_threshold
        ud_tests = (
            (self.ptb.word_ranks[ud_threshold], "postag", True),
            (self.ptb.word_ranks[ud_threshold], "NUM", False),
            (self.ptb.word_ranks[ud_threshold - 1], "postag", False),
        )

        for lemma, pos, res in ptb_tests:
            self.assertEqual(self.ptb.is_("sword", lemma, pos), res)
        for lemma, pos, res in ud_tests:
            self.assertEqual(self.ud.is_("sword", lemma, pos), res)
