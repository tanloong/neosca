#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from .base_tmpl import BaseTmpl
from .base_tmpl import text
from .base_tmpl import tree as tree_expected
from .base_tmpl import dir_stanford_parser
from neosca.parser import StanfordParser


class TestStanfordParser(BaseTmpl):
    def setUp(self):
        self.parser = StanfordParser(dir_stanford_parser)
        return super().setUp()

    def test_parse(self):
        tree = self.parser.parse(text)
        self.assertEqual(tree_expected, tree)
        text_never_false = """There was no possibility

of taking a walk that day."""
        text_never_true = """There was no possibility

of taking a walk that day ."""
        tree_correct = """(ROOT
  (S
    (NP (EX There))
    (VP (VBD was)
      (NP
        (NP (DT no) (NN possibility))
        (PP (IN of)
          (S
            (VP (VBG taking)
              (NP (DT a) (NN walk))
              (NP (DT that) (NN day)))))))
    (. .)))
"""
        self.assertEqual(
            tree_correct,
            self.parser.parse(text_never_false, newline_break="never", is_pretokenized=False),
        )
        self.assertEqual(
            tree_correct,
            self.parser.parse(text_never_true, newline_break="never", is_pretokenized=True),
        )
        self.assertNotEqual(
            tree_correct,
            self.parser.parse(text_never_false, newline_break="never", is_pretokenized=True),
        )
        self.assertNotEqual(
            tree_correct, self.parser.parse(text_never_false, newline_break="always")
        )
        self.assertNotEqual(
            tree_correct, self.parser.parse(text_never_false, newline_break="two")
        )
        text_always_false = """CHAPTER I
There was no possibility of taking a walk that day."""
        text_always_true = """CHAPTER I
There was no possibility of taking a walk that day ."""
        tree_correct = """(ROOT
  (S
    (VP (VB CHAPTER)
      (NP (PRP I)))))

(ROOT
  (S
    (NP (EX There))
    (VP (VBD was)
      (NP
        (NP (DT no) (NN possibility))
        (PP (IN of)
          (S
            (VP (VBG taking)
              (NP (DT a) (NN walk))
              (NP (DT that) (NN day)))))))
    (. .)))
"""
        self.assertEqual(
            tree_correct,
            self.parser.parse(text_always_false, newline_break="always", is_pretokenized=False),
        )
        self.assertEqual(
            tree_correct,
            self.parser.parse(text_always_true, newline_break="always", is_pretokenized=True),
        )
        self.assertNotEqual(
            tree_correct,
            self.parser.parse(text_always_false, newline_break="always", is_pretokenized=True),
        )
        self.assertNotEqual(
            tree_correct, self.parser.parse(text_always_false, newline_break="never")
        )
        self.assertNotEqual(
            tree_correct, self.parser.parse(text_always_false, newline_break="two")
        )
        text_two_false = """CHAPTER I

There was no possibility
of taking a walk that day."""
        text_two_true = """CHAPTER I

There was no possibility
of taking a walk that day ."""
        tree_correct = """(ROOT
  (S
    (VP (VB CHAPTER)
      (NP (PRP I)))))

(ROOT
  (S
    (NP (EX There))
    (VP (VBD was)
      (NP
        (NP (DT no) (NN possibility))
        (PP (IN of)
          (S
            (VP (VBG taking)
              (NP (DT a) (NN walk))
              (NP (DT that) (NN day)))))))
    (. .)))
"""
        self.assertEqual(
            tree_correct,
            self.parser.parse(text_two_false, newline_break="two", is_pretokenized=False),
        )
        self.assertEqual(
            tree_correct,
            self.parser.parse(text_two_true, newline_break="two", is_pretokenized=True),
        )
        self.assertNotEqual(
            tree_correct,
            self.parser.parse(text_two_false, newline_break="two", is_pretokenized=True),
        )
        self.assertNotEqual(
            tree_correct, self.parser.parse(text_two_false, newline_break="always")
        )
        self.assertNotEqual(
            tree_correct, self.parser.parse(text_two_false, newline_break="never")
        )

    def test_is_long(self):
        max_length = 100
        length_1 = 99
        length_2 = 100
        length_3 = 101
        self.assertFalse(self.parser._is_long(length_1, max_length))
        self.assertFalse(self.parser._is_long(length_2, max_length))
        self.assertTrue(self.parser._is_long(length_3, max_length))
        self.assertFalse(self.parser._is_long(length_3))
