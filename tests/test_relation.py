#!/usr/bin/env python3

from typing import List

from neosca.ns_tregex import relation as rel
from neosca.ns_tregex.tree import Tree

from .base_tmpl import BaseTmpl
from .base_tmpl import tree as tree_string


class TestRelation(BaseTmpl):
    def setUp(self):
        self.tree_string = tree_string
        self.t = next(Tree.fromstring(self.tree_string))
        return super().setUp()

    def test_dominates(self):
        nodes = self.compare_search_with_satisfies(self.t, rel.DOMINATES)
        observed = [node.label for node in nodes]
        # fmt: off
        expected = ["S", "NP", "EX", "There", "VP", "VBD", "was", "NP", "NP", "DT", "no", "NN", "possibility", "PP", "IN", "of", "S", "VP", "VBG", "taking", "NP", "DT", "a", "NN", "walk", "NP", "DT", "that", "NN", "day", ".", "."]
        # fmt: on
        self.assertListEqual(observed, expected)

    def test_ancestor_of_leaf(self):
        nodes = self.compare_search_with_satisfies(self.t, rel.ANCESTOR_OF_LEAF)
        observed = [node.label for node in nodes]
        # fmt: off
        expected = ["There", "was", "no", "possibility", "of", "taking", "a", "walk", "that", "day", "."]
        # fmt: on
        self.assertListEqual(observed, expected)

    def compare_search_with_satisfies(self, t: Tree, cls_) -> List[Tree]:
        nodes = list(cls_.searchNodeIterator(t))
        for node in nodes:
            self.assertTrue(cls_.satisfies(t, node))
        return nodes
