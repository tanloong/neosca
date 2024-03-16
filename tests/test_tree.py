#!/usr/bin/env python3

import re
import sys

from neosca.ns_tregex.tree import Tree

from .base_tmpl import BaseTmpl
from .base_tmpl import tree as tree_string


class TestTree(BaseTmpl):
    def setUp(self):
        self.tree_string = tree_string
        self.t = next(Tree.fromstring(self.tree_string))
        return super().setUp()

    def test_fromstring(self):
        tree_string1 = "(NP (EX There)"
        tree_string2 = "NP (EX There))"
        tree_string3 = "(NP (EX There)))"

        g1 = Tree.fromstring(tree_string1)
        # File "pytregex/src/pytregex/tree.py", line 398, in fromstring
        #  raise ValueError("incomplete tree (extra left parentheses in input)")
        self.assertRaises(ValueError, next, g1)

        g2 = Tree.fromstring(tree_string2)
        next(g2)
        # File "pytregex/src/pytregex/tree.py", line 378, in fromstring
        #  ValueError: failed to build tree from string with extra non-matching right parentheses
        self.assertRaises(ValueError, next, g2)

        g3 = Tree.fromstring(tree_string3)
        next(g3)
        # File "pytregex/src/pytregex/tree.py", line 378, in fromstring
        #  ValueError: failed to build tree from string with extra non-matching right parentheses
        self.assertRaises(ValueError, next, g3)

        # make sure that extra levels of root with None label has been removed
        self.assertEqual(next(Tree.fromstring(f"(({tree_string}))")), next(Tree.fromstring(tree_string)))

    def test_set_label(self):
        tree = next(Tree.fromstring(self.tree_string))
        new_label = "TOOR"  # inverse of ROOT
        tree.set_label(new_label)
        self.assertEqual(tree.label, new_label)

        self.assertRaises(TypeError, tree.set_label, [new_label])

    def test_eq(self):
        from copy import deepcopy

        tree = next(Tree.fromstring(self.tree_string))

        # compare Tree with other classes
        self.assertNotEqual(tree, "non-Tree object")

        # compare trees with different labels
        tree2 = deepcopy(tree)
        self.assertEqual(tree, tree2)
        tree2.set_label("non-existing label")
        self.assertNotEqual(tree, tree2)

        # compare trees with the same label but different number of children
        tree2.set_label("ROOT")
        tree.set_label("ROOT")
        self.assertEqual(tree, tree2)
        tree2.children.append(Tree())
        self.assertNotEqual(tree, tree2)

        # compare trees with the same label, the same number of children, but different child label
        tree.children.append(Tree())
        self.assertEqual(tree, tree2)
        tree2.children[0].set_label("non-existing label for child")
        self.assertNotEqual(tree, tree2)

    def test_getitem(self):
        cases = [
            (self.t[0], self.t.children[0]),
            (self.t[0, 0], self.t.children[0].children[0]),
            (self.t[0, 0], self.t[0][0]),
            (self.t[[]], self.t),
            (self.t[[0]], self.t.children[0]),
            (self.t[[0, 0]], self.t.children[0].children[0]),
            (self.t[[0, 0]], self.t[0, 0]),
        ]
        for elem1, elem2 in cases:
            self.assertIs(elem1, elem2)

        self.assertRaises(TypeError, self.t.__getitem__, "string")

    def test_len(self):
        tree = next(Tree.fromstring(self.tree_string))
        self.assertEqual(len(tree), len(tree.children))

    def test_numChildren(self):
        tree = next(Tree.fromstring(self.tree_string))
        self.assertEqual(tree.numChildren(), len(tree.children))

    def test_sister_index(self):
        tree = Tree()  # label=None, children=[], parent=None
        self.assertEqual(-1, tree.get_sister_index())

        self.assertEqual(self.t[0].get_sister_index(), 0)
        self.assertEqual(self.t[-1].get_sister_index(), len(self.t.children) - 1)

        tree_S = Tree("S", children=[Tree("NP"), Tree("VP")])
        tree_VP = tree_S.children.pop()
        self.assertEqual(-1, tree_VP.get_sister_index())

    def test_isLeaf(self):
        tree = Tree()
        self.assertTrue(tree.isLeaf())

        tree.children.append(Tree())
        self.assertFalse(tree.isLeaf())

    def test_left_sisters(self):
        self.assertIsNone(self.t[0].left_sisters())
        self.assertEqual(self.t[0, 1, 1].left_sisters(), self.t[0, 1][:1])

    def test_right_sisters(self):
        self.assertIsNone(self.t[0].right_sisters())
        self.assertEqual(self.t[0, 1, 0].right_sisters(), self.t[0, 1][1:])

    def test_is_preterminal(self):
        tree = Tree()
        self.assertFalse(tree.is_preterminal())

        tree.children.append(Tree())
        self.assertTrue(tree.is_preterminal())

        tree.children.append(Tree())
        self.assertFalse(tree.is_preterminal())

    def test_tostring(self):
        tree = next(Tree.fromstring(self.tree_string))
        # suppress onto one line
        tree_string = re.sub(r"\n\s+", " ", self.tree_string.strip())
        self.assertEqual(tree.tostring(), tree_string)

    def test_root(self):
        child = self.t[0]
        grandchild = self.t[0, 0]
        self.assertIs(child.getRoot(), self.t)
        self.assertIs(grandchild.getRoot(), self.t)

    def test_preorder_iter(self):
        # fmt: off
        expected = ["ROOT", "S", "NP", "EX", "There", "VP", "VBD", "was", "NP", "NP", "DT", "no", "NN", "possibility", "PP", "IN", "of", "S", "VP", "VBG", "taking", "NP", "DT", "a", "NN", "walk", "NP", "DT", "that", "NN", "day", ".", "."]
        # fmt: on
        observed = [node.label for node in self.t.preorder_iter()]
        self.assertListEqual(observed, expected)

    def test_get_terminal_labels(self):
        observed = self.t.get_terminal_labels()
        expected = ["There", "was", "no", "possibility", "of", "taking", "a", "walk", "that", "day", "."]
        self.assertListEqual(observed, expected)

    def test_get_tagged_terminal_labels(self):
        observed = self.t.get_tagged_terminal_labels()
        # fmt: off
        expected = ["There/EX", "was/VBD", "no/DT", "possibility/NN", "of/IN", "taking/VBG", "a/DT", "walk/NN", "that/DT", "day/NN", "./."]
        # fmt: on
        self.assertListEqual(observed, expected)

    def test_get_leaves(self):
        nodes = self.t.getLeaves()
        for node in nodes:
            self.assertTrue(node.isLeaf())

    def test_height(self):
        t = Tree()
        self.assertEqual(t.height(), 1)

        self.assertEqual(self.t.height(), 10)

    def test_deep_tree(self):
        # Set the maximum recursion depth to 2000
        limit = 1000
        sys.setrecursionlimit(limit)

        depth = limit + 100
        s_open = " ".join(f"({i}" for i in range(depth))
        s_close = " ".join(")" for _ in range(depth))
        s = s_open + " " + s_close

        # Test occasions where RecursionError should be avoided
        # Building deep tree
        t = next(Tree.fromstring(s))
        # Querying deep tree
        t.getLeaves()
        t.height()
        t.get_terminal_labels()
        t.get_tagged_terminal_labels()
