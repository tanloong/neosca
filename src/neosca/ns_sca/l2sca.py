#!/usr/bin/env python3

from collections.abc import Generator

from neosca.ns_tregex.node_descriptions import Node_Any, Node_Text
from neosca.ns_tregex.relation import (
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
from neosca.ns_tregex.tree import Tree


class Abstract_Searcher:
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        # The same node can be yieleded multiple times in two cases:
        #  echo '(A (a) (a))' | tregex.sh 'A < a'       # 'A' is matched twice
        #  echo '(A (a) (b))' | tregex.sh 'A [<a | <b]' # 'A' is matched twice
        #  Remeber to filter the generated nodes of this func if unique nodes are wanted.
        raise NotImplementedError()


class S(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        ROOT !> __
        """
        # Don't have to iterate the tree because descendants won't match
        if not Node_Text.satisfies(t, "ROOT"):
            return
        if not any(Node_Any.satisfies(node) for node in CHILD_OF.searchNodeIterator(t)):
            yield t


class VP1(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        VP > S|SINV|SQ
        """
        for candidate in t.preorder_iter():
            if not Node_Text.satisfies(candidate, "VP"):
                continue
            for _ in filter(
                lambda node: Node_Text.in_(node, ("S", "SINV", "SQ")),
                CHILD_OF.searchNodeIterator(candidate),
            ):
                yield candidate


class VP2(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        MD|VBZ|VBP|VBD > (SQ !< VP)
        """
        for candidate in t.preorder_iter():
            if not Node_Text.in_(candidate, ("MD", "VBZ", "VBP", "VBD")):
                continue
            for sq in filter(
                lambda node: Node_Text.satisfies(node, "SQ"),
                CHILD_OF.searchNodeIterator(candidate),
            ):
                if not any(Node_Text.satisfies(node, "VP") for node in PARENT_OF.searchNodeIterator(sq)):
                    yield candidate


class C1(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]
        """
        for candidate in t.preorder_iter():
            if not Node_Text.in_(candidate, ("S", "SINV", "SQ")):
                continue
            # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
            for _ in filter(
                lambda node: Node_Text.satisfies(node, "ROOT"),
                CHILD_OF.searchNodeIterator(candidate),
            ):
                for vp in filter(
                    lambda node: Node_Text.satisfies(node, "VP"),
                    HAS_LEFTMOST_CHILD.searchNodeIterator(candidate),
                ):
                    for _ in filter(
                        lambda node: Node_Text.satisfies(node, "VB"),
                        IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                    ):
                        yield candidate
            # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
            for _ in filter(
                lambda node: Node_Text.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                IMMEDIATELY_HEADED_BY.searchNodeIterator(candidate),
            ):
                yield candidate
            # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
            for vp in filter(
                lambda node: Node_Text.satisfies(node, "VP"),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                # Branch 3.1: S|SINV|SQ < (VP <# MD|VBP|VBZ|VBD)
                for _ in filter(
                    lambda node: Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                    IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                ):
                    yield candidate
                # Branch 3.2: S|SINV|SQ < (VP < CC < (VP <# MD|VBP|VBZ|VBD))
                for _ in filter(lambda node: Node_Text.satisfies(node, "CC"), PARENT_OF.searchNodeIterator(vp)):
                    for vp2 in filter(
                        lambda node: Node_Text.satisfies(node, "VP"),
                        PARENT_OF.searchNodeIterator(vp),
                    ):
                        for _ in filter(
                            lambda node: Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                            IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2),
                        ):
                            yield candidate


class C2(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        FRAG > ROOT !<< (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])
        """
        for candidate in t.preorder_iter():
            if not Node_Text.satisfies(candidate, "FRAG"):
                continue
            if not any(Node_Text.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(candidate)):
                continue

            is_satisfied = True
            for s in filter(
                lambda node: Node_Text.in_(node, ("S", "SINV", "SQ")),
                DOMINATES.searchNodeIterator(candidate),
            ):
                # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
                if any(Node_Text.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(s)) and any(
                    Node_Text.satisfies(node, "VB")
                    for vp in filter(
                        lambda node: Node_Text.satisfies(node, "VP"),
                        HAS_LEFTMOST_CHILD.searchNodeIterator(s),
                    )
                    for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(vp)
                ):
                    is_satisfied = False
                    break
                # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                if any(
                    Node_Text.in_(node, ("MD", "VBZ", "VBP", "VBD"))
                    for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(s)
                ):
                    is_satisfied = False
                    break
                # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                for vp in filter(lambda node: Node_Text.satisfies(node, "VP"), PARENT_OF.searchNodeIterator(s)):
                    if any(
                        Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD"))
                        for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(vp)
                    ):
                        is_satisfied = False
                        break
                    if any(
                        Node_Text.satisfies(node, "CC") for node in PARENT_OF.searchNodeIterator(vp)
                    ) and any(
                        Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD"))
                        for vp2 in filter(
                            lambda node: Node_Text.satisfies(node, "VP"),
                            PARENT_OF.searchNodeIterator(vp),
                        )
                        for node in IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2)
                    ):
                        is_satisfied = False
                        break
            if is_satisfied:
                yield candidate


class T1(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
        """
        for candidate in t.preorder_iter():
            if not Node_Text.in_(candidate, ("S", "SBARQ", "SINV", "SQ")):
                continue
            # Branch 1: S|SBARQ|SINV|SQ > ROOT
            for node in CHILD_OF.searchNodeIterator(candidate):
                if Node_Text.satisfies(node, "ROOT"):
                    yield candidate
            # Branch 2: S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
            for _ in filter(
                lambda node: Node_Text.in_(node, ("S", "SBARQ", "SINV", "SQ")),
                RIGHT_SISTER_OF.searchNodeIterator(candidate),
            ):
                if not any(
                    Node_Text.in_(node2, ("SBAR", "VP")) for node2 in DOMINATED_BY.searchNodeIterator(candidate)
                ):
                    yield candidate


class T2(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])
        """
        for candidate in t.preorder_iter():
            if not Node_Text.satisfies(candidate, "FRAG"):
                continue
            if not any(Node_Text.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(candidate)):
                continue
            is_satisfied = True
            for s in filter(
                lambda node: Node_Text.in_(node, ("S", "SBARQ", "SINV", "SQ")),
                DOMINATES.searchNodeIterator(candidate),
            ):
                # Branch 1: S|SBARQ|SINV|SQ > ROOT
                if any(Node_Text.satisfies(node, "ROOT") for node in CHILD_OF.searchNodeIterator(s)):
                    is_satisfied = False
                    break
                # Branch 2: S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
                if any(
                    Node_Text.in_(node, ("S", "SBARQ", "SINV", "SQ"))
                    for node in RIGHT_SISTER_OF.searchNodeIterator(s)
                ) and not any(
                    Node_Text.in_(node, ("SBAR", "VP")) for node in DOMINATED_BY.searchNodeIterator(s)
                ):
                    is_satisfied = False
                    break
            if is_satisfied:
                yield candidate


class CN1(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]
        """
        for candidate in t.preorder_iter():
            if not Node_Text.satisfies(candidate, "NP"):
                continue
            if any(Node_Text.satisfies(node, "NP") for node in CHILD_OF.searchNodeIterator(candidate)):
                continue
            # Branch 1: NP << JJ|POS|PP|S|VBG
            for _ in filter(
                lambda node: Node_Text.in_(node, ("JJ", "POS", "PP", "S", "VBG")),
                DOMINATES.searchNodeIterator(candidate),
            ):
                yield candidate
            # Branch 2: NP << (NP $++ NP !$+ CC)
            for np in filter(
                lambda node: Node_Text.satisfies(node, "NP"),
                DOMINATES.searchNodeIterator(candidate),
            ):
                for _ in filter(
                    lambda node: Node_Text.satisfies(node, "NP"),
                    LEFT_SISTER_OF.searchNodeIterator(np),
                ):
                    if not any(
                        Node_Text.satisfies(node, "CC")
                        for node in IMMEDIATE_LEFT_SISTER_OF.searchNodeIterator(np)
                    ):
                        yield candidate


class CN2(Abstract_Searcher):
    """
    SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]
    """

    @classmethod
    def conditionOneHelper(cls, t: Tree) -> Generator[Tree, None, None]:
        # Condition 1: SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S]
        # Branch 1.1: SBAR <# WHNP
        for _ in filter(
            lambda node: Node_Text.satisfies(node, "WHNP"),
            IMMEDIATELY_HEADED_BY.searchNodeIterator(t),
        ):
            yield t
        # Branch 1.2: SBAR <# (IN < That|that|For|for)
        for in_ in filter(
            lambda node: Node_Text.satisfies(node, "IN"),
            IMMEDIATELY_HEADED_BY.searchNodeIterator(t),
        ):
            for _ in filter(
                lambda node: Node_Text.in_(node, ("That", "that", "For", "for")),
                PARENT_OF.searchNodeIterator(in_),
            ):
                yield t
        # Branch 1.3: SBAR <, S
        for _ in filter(lambda node: Node_Text.satisfies(node, "S"), HAS_LEFTMOST_CHILD.searchNodeIterator(t)):
            yield t

    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        for candidate in t.preorder_iter():
            if not Node_Text.satisfies(candidate, "SBAR"):
                continue
            # Condition 1: SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S]
            for _ in cls.conditionOneHelper(candidate):
                # Condition 2: SBAR [$+ VP | > VP]
                for _ in filter(
                    lambda node: Node_Text.satisfies(node, "VP"),
                    IMMEDIATE_LEFT_SISTER_OF.searchNodeIterator(candidate),
                ):
                    yield candidate
                for _ in filter(
                    lambda node: Node_Text.satisfies(node, "VP"),
                    CHILD_OF.searchNodeIterator(candidate),
                ):
                    yield candidate


class CN3(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S < (VP <# VBG|TO) $+ VP
        """
        for candidate in t.preorder_iter():
            if not Node_Text.satisfies(candidate, "S"):
                continue
            # Condition 1: S < (VP <# VBG|TO)
            for vp in filter(
                lambda node: Node_Text.satisfies(node, "VP"),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                for _ in filter(
                    lambda node: Node_Text.in_(node, ("VBG", "TO")),
                    IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                ):
                    # Condition 2: S $+ VP
                    for _ in filter(
                        lambda node: Node_Text.satisfies(node, "VP"),
                        IMMEDIATE_LEFT_SISTER_OF.searchNodeIterator(candidate),
                    ):
                        yield candidate


class DC(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])
        """
        for candidate in t.preorder_iter():
            if not Node_Text.satisfies(candidate, "SBAR"):
                continue
            for s in filter(
                lambda node: Node_Text.in_(node, ("S", "SINV", "SQ")),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
                for _ in filter(lambda node: Node_Text.satisfies(node, "ROOT"), CHILD_OF.searchNodeIterator(s)):
                    for vp in filter(
                        lambda node: Node_Text.satisfies(node, "VP"),
                        HAS_LEFTMOST_CHILD.searchNodeIterator(s),
                    ):
                        for _ in filter(
                            lambda node: Node_Text.satisfies(node, "VB"),
                            IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                        ):
                            yield candidate
                # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                for _ in filter(
                    lambda node: Node_Text.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                    IMMEDIATELY_HEADED_BY.searchNodeIterator(s),
                ):
                    yield candidate
                # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                for vp in filter(lambda node: Node_Text.satisfies(node, "VP"), PARENT_OF.searchNodeIterator(s)):
                    # Branch 3.1: VP <# MD|VBP|VBZ|VBD
                    for _ in filter(
                        lambda node: Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                        IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                    ):
                        yield candidate
                    # Branch 3.2: VP < CC < (VP <# MD|VBP|VBZ|VBD)
                    for _ in filter(
                        lambda node: Node_Text.satisfies(node, "CC"),
                        PARENT_OF.searchNodeIterator(vp),
                    ):
                        for vp2 in filter(
                            lambda node: Node_Text.satisfies(node, "VP"),
                            PARENT_OF.searchNodeIterator(vp),
                        ):
                            for _ in filter(
                                lambda node: Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2),
                            ):
                                yield candidate


class CT(Abstract_Searcher):
    @classmethod
    def conditionOneHelper(cls, t: Tree) -> Generator[Tree, None, None]:
        # Condition 1: S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]]
        # Branch 1.1: S|SBARQ|SINV|SQ > ROOT
        # Branch 1.2: S|SBARQ|SINV|SQ $-- S|SBARQ|SINV|SQ !>> SBAR|VP
        for _ in filter(lambda node: Node_Text.satisfies(node, "ROOT"), CHILD_OF.searchNodeIterator(t)):
            yield t
        for _ in filter(
            lambda node: Node_Text.in_(node, ("S", "SBARQ", "SINV", "SQ")),
            RIGHT_SISTER_OF.searchNodeIterator(t),
        ):
            if not any(Node_Text.in_(node, ("SBAR", "VP")) for node in DOMINATED_BY.searchNodeIterator(t)):
                yield t

    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))
        """
        for candidate in t.preorder_iter():
            if not Node_Text.in_(candidate, ("S", "SBARQ", "SINV", "SQ")):
                continue
            for _ in cls.conditionOneHelper(candidate):
                # Condition 2: S|SBARQ|SINV|SQ << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))
                for sbar in filter(
                    lambda node: Node_Text.satisfies(node, "SBAR"),
                    DOMINATES.searchNodeIterator(candidate),
                ):
                    for s in filter(
                        lambda node: Node_Text.in_(node, ("S", "SINV", "SQ")),
                        PARENT_OF.searchNodeIterator(sbar),
                    ):
                        # Branch 2.1: S|SINV|SQ > ROOT <, (VP <# VB)
                        for _ in filter(
                            lambda node: Node_Text.satisfies(node, "ROOT"),
                            CHILD_OF.searchNodeIterator(s),
                        ):
                            for vp in filter(
                                lambda node: Node_Text.satisfies(node, "VP"),
                                HAS_LEFTMOST_CHILD.searchNodeIterator(s),
                            ):
                                for _ in filter(
                                    lambda node: Node_Text.satisfies(node, "VB"),
                                    IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                                ):
                                    yield candidate
                        # Branch 2.2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                        for _ in filter(
                            lambda node: Node_Text.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                            IMMEDIATELY_HEADED_BY.searchNodeIterator(s),
                        ):
                            yield candidate
                        # Branch 2.3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                        for vp in filter(
                            lambda node: Node_Text.satisfies(node, "VP"),
                            PARENT_OF.searchNodeIterator(s),
                        ):
                            # Branch 2.3.1: VP <# MD|VBP|VBZ|VBD
                            for _ in filter(
                                lambda node: Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                IMMEDIATELY_HEADED_BY.searchNodeIterator(vp),
                            ):
                                yield candidate
                            # Branch 2.3.2: VP < CC < (VP <# MD|VBP|VBZ|VBD)
                            for _ in filter(
                                lambda node: Node_Text.satisfies(node, "CC"),
                                PARENT_OF.searchNodeIterator(vp),
                            ):
                                for vp2 in filter(
                                    lambda node: Node_Text.satisfies(node, "VP"),
                                    PARENT_OF.searchNodeIterator(vp),
                                ):
                                    for _ in filter(
                                        lambda node: Node_Text.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                        IMMEDIATELY_HEADED_BY.searchNodeIterator(vp2),
                                    ):
                                        yield candidate


class CP(Abstract_Searcher):
    @classmethod
    def searchNodeIterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        ADJP|ADVP|NP|VP < CC
        """
        for candidate in t.preorder_iter():
            if not Node_Text.in_(candidate, ("ADJP", "ADVP", "NP", "VP")):
                continue
            for _ in filter(
                lambda node: Node_Text.satisfies(node, "CC"),
                PARENT_OF.searchNodeIterator(candidate),
            ):
                yield candidate
