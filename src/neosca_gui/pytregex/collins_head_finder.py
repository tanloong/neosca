#!/usr/bin/env python3

from typing import TYPE_CHECKING, List

from .abstract_collins_head_finder import AbstractCollinsHeadFinder

if TYPE_CHECKING:
    from .tree import Tree

# translated from https://github.com/stanfordnlp/CoreNLP/blob/main/src/edu/stanford/nlp/trees/CollinsHeadFinder.java
# last modified at May 24, 2019 (https://github.com/stanfordnlp/CoreNLP/commits/main/src/edu/stanford/nlp/trees/CollinsHeadFinder.java)


class CollinsHeadFinder(AbstractCollinsHeadFinder):
    def __init__(self, *categoriesToAvoid) -> None:
        super().__init__(*categoriesToAvoid)
        self.nonTerminalInfo = {  # {{{
            "ADJP": [
                [
                    "left",
                    "NNS",
                    "QP",
                    "NN",
                    "$",
                    "ADVP",
                    "JJ",
                    "VBN",
                    "VBG",
                    "ADJP",
                    "JJR",
                    "NP",
                    "JJS",
                    "DT",
                    "FW",
                    "RBR",
                    "RBS",
                    "SBAR",
                    "RB",
                ]
            ],
            "ADVP": [
                [
                    "right",
                    "RB",
                    "RBR",
                    "RBS",
                    "FW",
                    "ADVP",
                    "TO",
                    "CD",
                    "JJR",
                    "JJ",
                    "IN",
                    "NP",
                    "JJS",
                    "NN",
                ]
            ],
            "CONJP": [["right", "CC", "RB", "IN"]],
            "FRAG": [["right"]],  # crap
            "INTJ": [["left"]],
            "LST": [["right", "LS", ":"]],
            "NAC": [
                [
                    "left",
                    "NN",
                    "NNS",
                    "NNP",
                    "NNPS",
                    "NP",
                    "NAC",
                    "EX",
                    "$",
                    "CD",
                    "QP",
                    "PRP",
                    "VBG",
                    "JJ",
                    "JJS",
                    "JJR",
                    "ADJP",
                    "FW",
                ]
            ],
            "NX": [["left"]],  # crap
            "PP": [["right", "IN", "TO", "VBG", "VBN", "RP", "FW"]],
            "PRN": [["left"]],
            "PRT": [["right", "RP"]],
            "QP": [
                [
                    "left",
                    "$",
                    "IN",
                    "NNS",
                    "NN",
                    "JJ",
                    "RB",
                    "DT",
                    "CD",
                    "NCD",
                    "QP",
                    "JJR",
                    "JJS",
                ]
            ],
            "RRC": [["right", "VP", "NP", "ADVP", "ADJP", "PP"]],
            "S": [["left", "TO", "IN", "VP", "S", "SBAR", "ADJP", "UCP", "NP"]],
            "SBAR": [
                [
                    "left",
                    "WHNP",
                    "WHPP",
                    "WHADVP",
                    "WHADJP",
                    "IN",
                    "DT",
                    "S",
                    "SQ",
                    "SINV",
                    "SBAR",
                    "FRAG",
                ]
            ],
            "SBARQ": [["left", "SQ", "S", "SINV", "SBARQ", "FRAG"]],
            "SINV": [["left", "VBZ", "VBD", "VBP", "VB", "MD", "VP", "S", "SINV", "ADJP", "NP"]],
            "SQ": [["left", "VBZ", "VBD", "VBP", "VB", "MD", "VP", "SQ"]],
            "UCP": [["right"]],
            "VP": [
                [
                    "left",
                    "TO",
                    "VBD",
                    "VBN",
                    "MD",
                    "VBZ",
                    "VB",
                    "VBG",
                    "VBP",
                    "AUX",
                    "AUXG",
                    "VP",
                    "ADJP",
                    "NN",
                    "NNS",
                    "NP",
                ]
            ],
            "WHADJP": [["left", "CC", "WRB", "JJ", "ADJP"]],
            "WHADVP": [["right", "CC", "WRB"]],
            "WHNP": [["left", "WDT", "WP", "WP$", "WHADJP", "WHPP", "WHNP"]],
            "WHPP": [["right", "IN", "TO", "FW"]],
            "X": [["right"]],  # crap rule
            "NP": [
                ["rightdis", "NN", "NNP", "NNPS", "NNS", "NX", "POS", "JJR"],
                ["left", "NP"],
                ["rightdis", "$", "ADJP", "PRN"],
                ["right", "CD"],
                ["rightdis", "JJ", "JJS", "RB", "QP"],
            ],
            "TYPO": [["left"]],  # another crap rule, for Brown (Roger)
            "EDITED": [["left"]],  # crap rule for Switchboard (if don't delete EDITED nodes)
            "XS": [["right", "IN"]],  # rule for new structure in QP
        }  # }}}

    def postOperationFix(self, headIdx: int, daughterTrees: List["Tree"]) -> int:
        if headIdx >= 2:
            prevLab = daughterTrees[headIdx - 1].label
            if prevLab == "CC" or prevLab == "CONJP":
                newHeadIdx = headIdx - 2
                t = daughterTrees[newHeadIdx]
                while newHeadIdx >= 0 and t.is_pre_terminal and t.label in self.pennPunctTags:
                    newHeadIdx -= 1
                if newHeadIdx >= 0:
                    headIdx = newHeadIdx
        return headIdx
