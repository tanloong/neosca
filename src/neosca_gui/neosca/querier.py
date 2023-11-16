#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import re
import shutil
import sys
from io import BytesIO
from tokenize import NAME, NUMBER, PLUS, tokenize, untokenize
from typing import TYPE_CHECKING, Generator, List

from ..pytregex.node_descriptions import NODE_ANY, NODE_TEXT
from ..pytregex.relation import (
    CHILD_OF,
    DOMINATED_BY,
    DOMINATES,
    HAS_LEFTMOST_CHILD,
    IMMEDIATE_LEFT_SISTER_OF,
    IMMEDIATELY_HEADED_BY,
    LEFT_SISTER_OF,
    PARENT_OF,
    RIGHT_SISTER_OF,
)
from ..pytregex.tree import Tree
from .scaexceptions import CircularDefinitionError, InvalidSourceError

if TYPE_CHECKING:
    from .structure_counter import StructureCounter

class L2SCA_Abstract_Structure:  # {{{
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        # The same node can be yieleded multiple times in two cases:
        #  echo '(A (a) (a))' | tregex.sh 'A < a'       # 'A' is matched twice
        #  echo '(A (a) (b))' | tregex.sh 'A [<a | <b]' # 'A' is matched twice
        #  Remeber to filter the generated nodes of this func if unique nodes are wanted.
        raise NotImplementedError()


class L2SCA_S(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        ROOT !> __
        """
        # Don't have to iterate the tree because descendants won't match
        if not NODE_TEXT.satisfies(t, "ROOT"):
            return
        if not any(NODE_ANY.satisfies(node) for node in CHILD_OF.searchNodeIterator(t)):
            yield t


class L2SCA_VP1(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        VP > S|SINV|SQ
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.satisfies(candidate, "VP"):
                continue
            for _ in filter(
                lambda node: NODE_TEXT.in_(node, ("S", "SINV", "SQ")),
                CHILD_OF.searchNodeIterator(candidate),
            ):
                yield candidate


class L2SCA_VP2(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        MD|VBZ|VBP|VBD > (SQ !< VP)
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.in_(candidate, ("MD", "VBZ", "VBP", "VBD")):
                continue
            for sq in filter(
                lambda node: NODE_TEXT.satisfies(node, "SQ"),
                CHILD_OF.searchNodeIterator(candidate),
            ):
                if not any(NODE_TEXT.satisfies(node, "VP") for node in PARENT_OF.searchNodeIterator(sq)):
                    yield candidate


class L2SCA_C1(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.in_(candidate, ("S", "SINV", "SQ")):
                continue
            # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
            for _ in filter(
                lambda node: NODE_TEXT.satisfies(node, "ROOT"),
                CHILD_OF.searchNodeIterator(candidate),
            ):
                for vp in filter(
                    lambda node: NODE_TEXT.satisfies(node, "VP"),
                    HAS_LEFTMOST_CHILD.searchNodeIterator(candidate),
                ):
                    for _ in filter(
                        lambda node: NODE_TEXT.satisfies(node, "VB"),
                        IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                    ):
                        yield candidate
            # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
            for _ in filter(
                lambda node: NODE_TEXT.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                IMMEDIATELY_HEADED_BY.searchNodeIterator(candidate),
            ):
                yield candidate
            # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
            for vp in filter(
                lambda node: NODE_TEXT.satisfies(node, "VP"),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                # Branch 3.1: S|SINV|SQ < (VP <# MD|VBP|VBZ|VBD)
                for _ in filter(
                    lambda node: NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                    IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                ):
                    yield candidate
                # Branch 3.2: S|SINV|SQ < (VP < CC < (VP <# MD|VBP|VBZ|VBD))
                for _ in filter(lambda node: NODE_TEXT.satisfies(node, "CC"), PARENT_OF.searchNodeIterator(vp)):
                    for vp2 in filter(
                        lambda node: NODE_TEXT.satisfies(node, "VP"),
                        PARENT_OF.searchNodeIterator(vp),
                    ):
                        for _ in filter(
                            lambda node: NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                            IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2),
                        ):
                            yield candidate


class L2SCA_C2(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        FRAG > ROOT !<< (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.satisfies(candidate, "FRAG"):
                continue
            if not any(NODE_TEXT.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(candidate)):
                continue

            is_satisfied = True
            for s in filter(
                lambda node: NODE_TEXT.in_(node, ("S", "SINV", "SQ")),
                DOMINATES.searchNodeIterator(candidate),
            ):
                # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
                if any(NODE_TEXT.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(s)) and any(
                    NODE_TEXT.satisfies(node, "VB")
                    for vp in filter(
                        lambda node: NODE_TEXT.satisfies(node, "VP"),
                        HAS_LEFTMOST_CHILD.searchNodeIterator(s),
                    )
                    for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(vp)
                ):
                    is_satisfied = False
                    break
                # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                if any(
                    NODE_TEXT.in_(node, ("MD", "VBZ", "VBP", "VBD"))
                    for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(s)
                ):
                    is_satisfied = False
                    break
                # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                for vp in filter(lambda node: NODE_TEXT.satisfies(node, "VP"), PARENT_OF.searchNodeIterator(s)):
                    if any(
                        NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD"))
                        for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(vp)
                    ):
                        is_satisfied = False
                        break
                    if any(NODE_TEXT.satisfies(node, "CC") for node in PARENT_OF.searchNodeIterator(vp)) and any(
                        NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD"))
                        for vp2 in filter(
                            lambda node: NODE_TEXT.satisfies(node, "VP"),
                            PARENT_OF.searchNodeIterator(vp),
                        )
                        for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2)
                    ):
                        is_satisfied = False
                        break
            if is_satisfied:
                yield candidate


class L2SCA_T1(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.in_(candidate, ("S", "SBARQ", "SINV", "SQ")):
                continue
            # Branch 1: S|SBARQ|SINV|SQ > ROOT
            for node in CHILD_OF.searchNodeIterator(candidate):
                if NODE_TEXT.satisfies(node, "ROOT"):
                    yield candidate
            # Branch 2: S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
            for _ in filter(
                lambda node: NODE_TEXT.in_(node, ("S", "SBARQ", "SINV", "SQ")),
                RIGHT_SISTER_OF.searchNodeIterator(candidate),
            ):
                if not any(
                    NODE_TEXT.in_(node2, ("SBAR", "VP")) for node2 in DOMINATED_BY.searchNodeIterator(candidate)
                ):
                    yield candidate


class L2SCA_T2(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.satisfies(candidate, "FRAG"):
                continue
            if not any(NODE_TEXT.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(candidate)):
                continue
            is_satisfied = True
            for s in filter(
                lambda node: NODE_TEXT.in_(node, ("S", "SBARQ", "SINV", "SQ")),
                DOMINATES.searchNodeIterator(candidate),
            ):
                # Branch 1: S|SBARQ|SINV|SQ > ROOT
                if any(NODE_TEXT.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(s)):
                    is_satisfied = False
                    break
                # Branch 2: S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
                if any(
                    NODE_TEXT.in_(node, ("S", "SBARQ", "SINV", "SQ"))
                    for node in RIGHT_SISTER_OF.searchNodeIterator(s)
                ) and not any(NODE_TEXT.in_(node, ("SBAR", "VP")) for node in DOMINATED_BY.searchNodeIterator(s)):
                    is_satisfied = False
                    break
            if is_satisfied:
                yield candidate


class L2SCA_CN1(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.satisfies(candidate, "NP"):
                continue
            if any(NODE_TEXT.satisfies(node, "NP") for node in CHILD_OF.searchNodeIterator(candidate)):
                continue
            # Branch 1: NP << JJ|POS|PP|S|VBG
            for _ in filter(
                lambda node: NODE_TEXT.in_(node, ("JJ", "POS", "PP", "S", "VBG")),
                DOMINATES.searchNodeIterator(candidate),
            ):
                yield candidate
            # Branch 2: NP << (NP $++ NP !$+ CC)
            for np in filter(
                lambda node: NODE_TEXT.satisfies(node, "NP"),
                DOMINATES.searchNodeIterator(candidate),
            ):
                for _ in filter(
                    lambda node: NODE_TEXT.satisfies(node, "NP"),
                    LEFT_SISTER_OF.searchNodeIterator(np),
                ):
                    if not any(
                        NODE_TEXT.satisfies(node, "CC")
                        for node in IMMEDIATE_LEFT_SISTER_OF.searchNodeIterator(np)
                    ):
                        yield candidate


class L2SCA_CN2(L2SCA_Abstract_Structure):
    @classmethod
    def conditionOneHelper(cls, t: Tree) -> Generator[Tree, None, None]:
        # Condition 1: SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S]
        # Branch 1.1: SBAR <# WHNP
        for _ in filter(
            lambda node: NODE_TEXT.satisfies(node, "WHNP"),
            IMMEDIATELY_HEADED_BY.searchNodeIterator(t),
        ):
            yield t
        # Branch 1.2: SBAR <# (IN < That|that|For|for)
        for in_ in filter(
            lambda node: NODE_TEXT.satisfies(node, "IN"),
            IMMEDIATELY_HEADED_BY.searchNodeIterator(t),
        ):
            for _ in filter(
                lambda node: NODE_TEXT.in_(node, ("That", "that", "For", "for")),
                PARENT_OF.searchNodeIterator(in_),
            ):
                yield t
        # Branch 1.3: SBAR <, S
        for _ in filter(lambda node: NODE_TEXT.satisfies(node, "S"), HAS_LEFTMOST_CHILD.searchNodeIterator(t)):
            yield t

    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.satisfies(candidate, "SBAR"):
                continue
            # Condition 1: SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S]
            for _ in cls.conditionOneHelper(candidate):
                # Condition 2: SBAR [$+ VP | > VP]
                for _ in filter(
                    lambda node: NODE_TEXT.satisfies(node, "VP"),
                    IMMEDIATE_LEFT_SISTER_OF.searchNodeIterator(candidate),
                ):
                    yield candidate
                for _ in filter(
                    lambda node: NODE_TEXT.satisfies(node, "VP"),
                    CHILD_OF.searchNodeIterator(candidate),
                ):
                    yield candidate


class L2SCA_CN3(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S < (VP <# VBG|TO) $+ VP
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.satisfies(candidate, "S"):
                continue
            # Condition 1: S < (VP <# VBG|TO)
            for vp in filter(
                lambda node: NODE_TEXT.satisfies(node, "VP"),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                for _ in filter(
                    lambda node: NODE_TEXT.in_(node, ("VBG", "TO")),
                    IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                ):
                    # Condition 2: S $+ VP
                    for _ in filter(
                        lambda node: NODE_TEXT.satisfies(node, "VP"),
                        IMMEDIATE_LEFT_SISTER_OF.searchNodeIterator(candidate),
                    ):
                        yield candidate


class L2SCA_DC(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.satisfies(candidate, "SBAR"):
                continue
            for s in filter(
                lambda node: NODE_TEXT.in_(node, ("S", "SINV", "SQ")),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
                for _ in filter(lambda node: NODE_TEXT.satisfies(node, "ROOT"), CHILD_OF.searchNodeIterator(s)):
                    for vp in filter(
                        lambda node: NODE_TEXT.satisfies(node, "VP"),
                        HAS_LEFTMOST_CHILD.searchNodeIterator(s),
                    ):
                        for _ in filter(
                            lambda node: NODE_TEXT.satisfies(node, "VB"),
                            IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                        ):
                            yield candidate
                # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                for _ in filter(
                    lambda node: NODE_TEXT.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                    IMMEDIATELY_HEADED_BY.searchNodeIterator(s),
                ):
                    yield candidate
                # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                for vp in filter(lambda node: NODE_TEXT.satisfies(node, "VP"), PARENT_OF.searchNodeIterator(s)):
                    # Branch 3.1: VP <# MD|VBP|VBZ|VBD
                    for _ in filter(
                        lambda node: NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                        IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                    ):
                        yield candidate
                    # Branch 3.2: VP < CC < (VP <# MD|VBP|VBZ|VBD)
                    for _ in filter(
                        lambda node: NODE_TEXT.satisfies(node, "CC"),
                        PARENT_OF.searchNodeIterator(vp),
                    ):
                        for vp2 in filter(
                            lambda node: NODE_TEXT.satisfies(node, "VP"),
                            PARENT_OF.searchNodeIterator(vp),
                        ):
                            for _ in filter(
                                lambda node: NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2),
                            ):
                                yield candidate


class L2SCA_CT(L2SCA_Abstract_Structure):
    @classmethod
    def conditionOneHelper(cls, t: Tree) -> Generator[Tree, None, None]:
        # Condition 1: S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]]
        # Branch 1.1: S|SBARQ|SINV|SQ > ROOT
        # Branch 1.2: S|SBARQ|SINV|SQ $-- S|SBARQ|SINV|SQ !>> SBAR|VP
        for _ in filter(lambda node: NODE_TEXT.satisfies(node, "ROOT"), CHILD_OF.searchNodeIterator(t)):
            yield t
        for _ in filter(
            lambda node: NODE_TEXT.in_(node, ("S", "SBARQ", "SINV", "SQ")),
            RIGHT_SISTER_OF.searchNodeIterator(t),
        ):
            if not any(NODE_TEXT.in_(node, ("SBAR", "VP")) for node in DOMINATED_BY.searchNodeIterator(t)):
                yield t

    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.in_(candidate, ("S", "SBARQ", "SINV", "SQ")):
                continue
            for _ in cls.conditionOneHelper(candidate):
                # Condition 2: S|SBARQ|SINV|SQ << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))
                for sbar in filter(
                    lambda node: NODE_TEXT.satisfies(node, "SBAR"),
                    DOMINATES.searchNodeIterator(candidate),
                ):
                    for s in filter(
                        lambda node: NODE_TEXT.in_(node, ("S", "SINV", "SQ")),
                        PARENT_OF.searchNodeIterator(sbar),
                    ):
                        # Branch 2.1: S|SINV|SQ > ROOT <, (VP <# VB)
                        for _ in filter(
                            lambda node: NODE_TEXT.satisfies(node, "ROOT"),
                            CHILD_OF.searchNodeIterator(s),
                        ):
                            for vp in filter(
                                lambda node: NODE_TEXT.satisfies(node, "VP"),
                                HAS_LEFTMOST_CHILD.searchNodeIterator(s),
                            ):
                                for _ in filter(
                                    lambda node: NODE_TEXT.satisfies(node, "VB"),
                                    IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                                ):
                                    yield candidate
                        # Branch 2.2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                        for _ in filter(
                            lambda node: NODE_TEXT.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                            IMMEDIATELY_HEADED_BY.searchNodeIterator(s),
                        ):
                            yield candidate
                        # Branch 2.3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                        for vp in filter(
                            lambda node: NODE_TEXT.satisfies(node, "VP"),
                            PARENT_OF.searchNodeIterator(s),
                        ):
                            # Branch 2.3.1: VP <# MD|VBP|VBZ|VBD
                            for _ in filter(
                                lambda node: NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                            ):
                                yield candidate
                            # Branch 2.3.2: VP < CC < (VP <# MD|VBP|VBZ|VBD)
                            for _ in filter(
                                lambda node: NODE_TEXT.satisfies(node, "CC"),
                                PARENT_OF.searchNodeIterator(vp),
                            ):
                                for vp2 in filter(
                                    lambda node: NODE_TEXT.satisfies(node, "VP"),
                                    PARENT_OF.searchNodeIterator(vp),
                                ):
                                    for _ in filter(
                                        lambda node: NODE_TEXT.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                        IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2),
                                    ):
                                        yield candidate


class L2SCA_CP(L2SCA_Abstract_Structure):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        ADJP|ADVP|NP|VP < CC
        """
        for candidate in t.preorder_iter():
            if not NODE_TEXT.in_(candidate, ("ADJP", "ADVP", "NP", "VP")):
                continue
            for _ in filter(
                lambda node: NODE_TEXT.satisfies(node, "CC"),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                yield candidate

            # }}}


class Ns_PyTregex:
    SNAME_CLS_MAPPING = {
        "S": L2SCA_S,
        "VP1": L2SCA_VP1,
        "VP2": L2SCA_VP2,
        "C1": L2SCA_C1,
        "C2": L2SCA_C2,
        "T1": L2SCA_T1,
        "T2": L2SCA_T2,
        "CN1": L2SCA_CN1,
        "CN2": L2SCA_CN2,
        "CN3": L2SCA_CN3,
        "DC": L2SCA_DC,
        "CT": L2SCA_CT,
        "CP": L2SCA_CP,
    }

    def get_matches(self, sname: str, trees: str) -> list:
        if sname not in self.SNAME_CLS_MAPPING:
            raise ValueError(f"{sname} is not yet supported in NeoSCA-GUI.")

        matches = []
        last_node = None
        for tree in Tree.fromstring(trees):
            for node in self.SNAME_CLS_MAPPING[sname].searchNodeIterator(tree):
                if node is last_node:
                    # implement Tregex's -o option: https://github.com/stanfordnlp/CoreNLP/blob/efc66a9cf49fecba219dfaa4025315ad966285cc/src/edu/stanford/nlp/trees/tregex/TregexPattern.java#L885
                    continue
                last_node = node
                span_string = node.span_string()
                matches.append(span_string)
        return matches

    @classmethod
    def check_circular_def(
        cls, descendant_sname: str, ancestor_snames: List[str], counter: "StructureCounter"
    ) -> None:
        if descendant_sname in ancestor_snames:
            circular_definition = ", ".join(
                f"{upstream_sname} = {counter.get_structure(upstream_sname).value_source}"
                for upstream_sname in ancestor_snames
            )
            raise CircularDefinitionError(f"Circular definition: {circular_definition}")
        else:
            logging.debug(
                "[StanfordTregex] Circular definition check passed: descendant"
                f" {descendant_sname} not in ancestors {ancestor_snames}"
            )

    def tokenize_value_source(
        self,
        value_source: str,
        counter: "StructureCounter",
        sname: str,
        trees: str,
        ancestor_snames: List[str],
    ) -> list:
        tokens = []
        g = tokenize(BytesIO(value_source.encode("utf-8")).readline)
        next(g)  # skip the "utf-8" token
        for toknum, tokval, *_ in g:
            if toknum == NAME:
                ancestor_snames.append(sname)
                Ns_PyTregex.check_circular_def(tokval, ancestor_snames, counter)

                self.set_value(counter, tokval, trees, ancestor_snames)
                if self.has_tregex_pattern(counter, tokval):
                    ancestor_snames.clear()

                tokens.append((toknum, f"counter.get_structure('{tokval}')"))
            elif toknum == NUMBER:
                tokens.append((toknum, tokval))
            elif tokval in ("+", "-", "*", "/", "(", ")"):
                tokens.append((toknum, tokval))
            # constrain value_source as only NAMEs and numberic ops to assure security for `eval`
            elif tokval != "":
                raise InvalidSourceError(f'Unexpected token: "{tokval}"')
        # append "+ 0" to force tokens evaluated as num if value_source contains just name of another Structure
        tokens.extend(((PLUS, "+"), (NUMBER, "0")))
        return tokens

    def has_tregex_pattern(self, counter: "StructureCounter", sname: str) -> bool:
        return counter.get_structure(sname).tregex_pattern is not None

    def set_value_from_pattern(self, counter: "StructureCounter", sname: str, trees: str):
        structure = counter.get_structure(sname)
        tregex_pattern = structure.tregex_pattern
        assert tregex_pattern is not None

        logging.info(
            f" Searching for {sname}"
            + (f" ({structure.description})..." if structure.description is not None else "...")
        )
        logging.debug(f" Searching for {tregex_pattern}")
        matched_subtrees = self.get_matches(sname, trees)
        counter.set_matches(sname, matched_subtrees)
        counter.set_value(sname, len(matched_subtrees))

    def set_value_from_source(
        self, counter: "StructureCounter", sname: str, trees: str, ancestor_snames: List[str]
    ) -> None:
        structure = counter.get_structure(sname)
        value_source = structure.value_source
        assert value_source is not None, f"value_source for {sname} is None."

        logging.info(
            f" Calculating {sname} "
            + (f"({structure.description}) " if structure.description is not None else "")
            + f"= {value_source}..."
        )
        tokens = self.tokenize_value_source(value_source, counter, sname, trees, ancestor_snames)
        value = eval(untokenize(tokens))
        counter.set_value(sname, value)

    def set_value(
        self,
        counter: "StructureCounter",
        sname: str,
        trees: str,
        ancestor_snames: List[str] = [],
    ) -> None:
        value = counter.get_value(sname)
        if value is not None:
            logging.debug(f"[StanfordTregex] {sname} has already been set as {value}, skipping...")
            return

        if sname == "W":
            logging.info(' Searching for "words"')
            value = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
            counter.set_value(sname, value)
            return

        if self.has_tregex_pattern(counter, sname):
            self.set_value_from_pattern(counter, sname, trees)
        else:
            self.set_value_from_source(counter, sname, trees, ancestor_snames)

    def set_all_values(self, counter: "StructureCounter", trees: str) -> None:
        for sname in counter.selected_measures:
            self.set_value(counter, sname, trees)

    def query(
        self,
        counter: "StructureCounter",
        trees: str,
        is_reserve_matched: bool = False,
        odir_matched: str = "",
        is_stdout: bool = False,
    ) -> "StructureCounter":
        self.set_all_values(counter, trees)

        if is_reserve_matched:  # pragma: no cover
            self.write_match_output(counter, odir_matched, is_stdout)
        return counter

    def write_match_output(
        self, counter: "StructureCounter", odir_matched: str = "", is_stdout: bool = False
    ) -> None:  # pragma: no cover
        bn_input = os_path.basename(counter.ifile)
        bn_input_noext = os_path.splitext(bn_input)[0]
        subodir_matched = os_path.join(odir_matched, bn_input_noext).strip()
        if not is_stdout:
            shutil.rmtree(subodir_matched, ignore_errors=True)
            os.makedirs(subodir_matched)
        for sname, structure in counter.sname_structure_map.items():
            matches = structure.matches
            if matches is None or len(matches) == 0:
                continue

            meta_data = (
                f"# name: {structure.name}\n"
                + f"# description: {structure.description}\n"
                + f"# pytregex_pattern: {structure.tregex_pattern}\n\n"
            )
            res = "\n".join(matches)
            # only accept alphanumeric chars, underscore, and hypen
            escaped_sname = re.sub(r"[^\w-]", "", sname.replace("/", "-per-"))
            matches_id = bn_input_noext + "-" + escaped_sname
            if not is_stdout:
                extension = ".txt"
                fn_match_output = os_path.join(subodir_matched, matches_id + extension)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(meta_data)
                    f.write(res)
            else:
                sys.stdout.write(matches_id + "\n")
                sys.stdout.write(meta_data)
                sys.stdout.write(res)
