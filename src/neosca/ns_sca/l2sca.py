#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections.abc import Generator

from ..ns_tregex.node_descriptions import NodeAny, NodeText
from ..ns_tregex.relation import (
    ChildOf,
    DominatedBy,
    Dominates,
    HasLeftmostChild,
    ImmediateLeftSisterOf,
    ImmediatelyHeadedBy,
    LeftSisterOf,
    ParentOf,
    RightSisterOf,
)
from ..ns_tregex.tree import Tree


class AbstractSearcher(ABC):
    @classmethod
    @abstractmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        # The same node can be yieleded multiple times in two cases:
        #  echo '(A (a) (a))' | tregex.sh 'A < a'       # 'A' is matched twice
        #  echo '(A (a) (b))' | tregex.sh 'A [<a | <b]' # 'A' is matched twice
        #  Remeber to filter the generated nodes of this func if unique nodes are wanted.
        raise NotImplementedError


class S(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        ROOT !> __
        """
        # Don't have to iterate the tree because descendants won't match
        if not NodeText.satisfies(t, "ROOT"):
            return
        if not any(NodeAny.satisfies(node) for node in ChildOf.search_node_iterator(t)):
            yield t


class VP1(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        VP > S|SINV|SQ
        """
        for candidate in t.visit():
            if not NodeText.satisfies(candidate, "VP"):
                continue
            for _ in filter(
                lambda node: NodeText.in_(node, ("S", "SINV", "SQ")),
                ChildOf.search_node_iterator(candidate),
            ):
                yield candidate


class VP2(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        MD|VBZ|VBP|VBD > (SQ !< VP)
        """
        for candidate in t.visit():
            if not NodeText.in_(candidate, ("MD", "VBZ", "VBP", "VBD")):
                continue
            for sq in filter(
                lambda node: NodeText.satisfies(node, "SQ"),
                ChildOf.search_node_iterator(candidate),
            ):
                if not any(NodeText.satisfies(node, "VP") for node in ParentOf.search_node_iterator(sq)):
                    yield candidate


class C1(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]
        """
        for candidate in t.visit():
            if not NodeText.in_(candidate, ("S", "SINV", "SQ")):
                continue
            # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
            for _ in filter(
                lambda node: NodeText.satisfies(node, "ROOT"),
                ChildOf.search_node_iterator(candidate),
            ):
                for vp in filter(
                    lambda node: NodeText.satisfies(node, "VP"),
                    HasLeftmostChild.search_node_iterator(candidate),
                ):
                    for _ in filter(
                        lambda node: NodeText.satisfies(node, "VB"),
                        ImmediatelyHeadedBy.search_node_iterator(vp),
                    ):
                        yield candidate
            # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
            for _ in filter(
                lambda node: NodeText.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                ImmediatelyHeadedBy.search_node_iterator(candidate),
            ):
                yield candidate
            # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
            for vp in filter(
                lambda node: NodeText.satisfies(node, "VP"),
                ParentOf.search_node_iterator(candidate),
            ):
                # Branch 3.1: S|SINV|SQ < (VP <# MD|VBP|VBZ|VBD)
                for _ in filter(
                    lambda node: NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                    ImmediatelyHeadedBy.search_node_iterator(vp),
                ):
                    yield candidate
                # Branch 3.2: S|SINV|SQ < (VP < CC < (VP <# MD|VBP|VBZ|VBD))
                for _ in filter(lambda node: NodeText.satisfies(node, "CC"), ParentOf.search_node_iterator(vp)):
                    for vp2 in filter(
                        lambda node: NodeText.satisfies(node, "VP"),
                        ParentOf.search_node_iterator(vp),
                    ):
                        for _ in filter(
                            lambda node: NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                            ImmediatelyHeadedBy.search_node_iterator(vp2),
                        ):
                            yield candidate


class C2(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        FRAG > ROOT !<< (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])
        """
        for candidate in t.visit():
            if not NodeText.satisfies(candidate, "FRAG"):
                continue
            if not any(NodeText.satisfies(node, "ROOT") for node in ChildOf.search_node_iterator(candidate)):
                continue

            is_satisfied = True
            for s in filter(
                lambda node: NodeText.in_(node, ("S", "SINV", "SQ")),
                Dominates.search_node_iterator(candidate),
            ):
                # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
                if any(NodeText.satisfies(node, "ROOT") for node in ChildOf.search_node_iterator(s)) and any(
                    NodeText.satisfies(node, "VB")
                    for vp in filter(
                        lambda node: NodeText.satisfies(node, "VP"),
                        HasLeftmostChild.search_node_iterator(s),
                    )
                    for node in ImmediatelyHeadedBy.search_node_iterator(vp)
                ):
                    is_satisfied = False
                    break
                # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                if any(
                    NodeText.in_(node, ("MD", "VBZ", "VBP", "VBD"))
                    for node in ImmediatelyHeadedBy.search_node_iterator(s)
                ):
                    is_satisfied = False
                    break
                # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                for vp in filter(lambda node: NodeText.satisfies(node, "VP"), ParentOf.search_node_iterator(s)):
                    if any(
                        NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD"))
                        for node in ImmediatelyHeadedBy.search_node_iterator(vp)
                    ):
                        is_satisfied = False
                        break
                    if any(
                        NodeText.satisfies(node, "CC") for node in ParentOf.search_node_iterator(vp)
                    ) and any(
                        NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD"))
                        for vp2 in filter(
                            lambda node: NodeText.satisfies(node, "VP"),
                            ParentOf.search_node_iterator(vp),
                        )
                        for node in ImmediatelyHeadedBy.search_node_iterator(vp2)
                    ):
                        is_satisfied = False
                        break
            if is_satisfied:
                yield candidate


class T1(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
        """
        for candidate in t.visit():
            if not NodeText.in_(candidate, ("S", "SBARQ", "SINV", "SQ")):
                continue
            # Branch 1: S|SBARQ|SINV|SQ > ROOT
            for node in ChildOf.search_node_iterator(candidate):
                if NodeText.satisfies(node, "ROOT"):
                    yield candidate
            # Branch 2: S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
            for _ in filter(
                lambda node: NodeText.in_(node, ("S", "SBARQ", "SINV", "SQ")),
                RightSisterOf.search_node_iterator(candidate),
            ):
                if not any(
                    NodeText.in_(node2, ("SBAR", "VP")) for node2 in DominatedBy.search_node_iterator(candidate)
                ):
                    yield candidate


class T2(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])
        """
        for candidate in t.visit():
            if not NodeText.satisfies(candidate, "FRAG"):
                continue
            if not any(NodeText.satisfies(node, "ROOT") for node in ChildOf.search_node_iterator(candidate)):
                continue
            is_satisfied = True
            for s in filter(
                lambda node: NodeText.in_(node, ("S", "SBARQ", "SINV", "SQ")),
                Dominates.search_node_iterator(candidate),
            ):
                # Branch 1: S|SBARQ|SINV|SQ > ROOT
                if any(NodeText.satisfies(node, "ROOT") for node in ChildOf.search_node_iterator(s)):
                    is_satisfied = False
                    break
                # Branch 2: S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
                if any(
                    NodeText.in_(node, ("S", "SBARQ", "SINV", "SQ"))
                    for node in RightSisterOf.search_node_iterator(s)
                ) and not any(
                    NodeText.in_(node, ("SBAR", "VP")) for node in DominatedBy.search_node_iterator(s)
                ):
                    is_satisfied = False
                    break
            if is_satisfied:
                yield candidate


class CN1(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]
        """
        for candidate in t.visit():
            if not NodeText.satisfies(candidate, "NP"):
                continue
            if any(NodeText.satisfies(node, "NP") for node in ChildOf.search_node_iterator(candidate)):
                continue
            # Branch 1: NP << JJ|POS|PP|S|VBG
            for _ in filter(
                lambda node: NodeText.in_(node, ("JJ", "POS", "PP", "S", "VBG")),
                Dominates.search_node_iterator(candidate),
            ):
                yield candidate
            # Branch 2: NP << (NP $++ NP !$+ CC)
            for np in filter(
                lambda node: NodeText.satisfies(node, "NP"),
                Dominates.search_node_iterator(candidate),
            ):
                for _ in filter(
                    lambda node: NodeText.satisfies(node, "NP"),
                    LeftSisterOf.search_node_iterator(np),
                ):
                    if not any(
                        NodeText.satisfies(node, "CC")
                        for node in ImmediateLeftSisterOf.search_node_iterator(np)
                    ):
                        yield candidate


class CN2(AbstractSearcher):
    @classmethod
    def condition_one_helper(cls, t: Tree) -> Generator[Tree, None, None]:
        # Condition 1: SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S]
        # Branch 1.1: SBAR <# WHNP
        for _ in filter(
            lambda node: NodeText.satisfies(node, "WHNP"),
            ImmediatelyHeadedBy.search_node_iterator(t),
        ):
            yield t
        # Branch 1.2: SBAR <# (IN < That|that|For|for)
        for in_ in filter(
            lambda node: NodeText.satisfies(node, "IN"),
            ImmediatelyHeadedBy.search_node_iterator(t),
        ):
            for _ in filter(
                lambda node: NodeText.in_(node, ("That", "that", "For", "for")),
                ParentOf.search_node_iterator(in_),
            ):
                yield t
        # Branch 1.3: SBAR <, S
        for _ in filter(lambda node: NodeText.satisfies(node, "S"), HasLeftmostChild.search_node_iterator(t)):
            yield t

    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]
        """
        for candidate in t.visit():
            if not NodeText.satisfies(candidate, "SBAR"):
                continue
            # Condition 1: SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S]
            for _ in cls.condition_one_helper(candidate):
                # Condition 2: SBAR [$+ VP | > VP]
                for _ in filter(
                    lambda node: NodeText.satisfies(node, "VP"),
                    ImmediateLeftSisterOf.search_node_iterator(candidate),
                ):
                    yield candidate
                for _ in filter(
                    lambda node: NodeText.satisfies(node, "VP"),
                    ChildOf.search_node_iterator(candidate),
                ):
                    yield candidate


class CN3(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S < (VP <# VBG|TO) $+ VP
        """
        for candidate in t.visit():
            if not NodeText.satisfies(candidate, "S"):
                continue
            # Condition 1: S < (VP <# VBG|TO)
            for vp in filter(
                lambda node: NodeText.satisfies(node, "VP"),
                ParentOf.search_node_iterator(candidate),
            ):
                for _ in filter(
                    lambda node: NodeText.in_(node, ("VBG", "TO")),
                    ImmediatelyHeadedBy.search_node_iterator(vp),
                ):
                    # Condition 2: S $+ VP
                    for _ in filter(
                        lambda node: NodeText.satisfies(node, "VP"),
                        ImmediateLeftSisterOf.search_node_iterator(candidate),
                    ):
                        yield candidate


class DC(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])
        """
        for candidate in t.visit():
            if not NodeText.satisfies(candidate, "SBAR"):
                continue
            for s in filter(
                lambda node: NodeText.in_(node, ("S", "SINV", "SQ")),
                ParentOf.search_node_iterator(candidate),
            ):
                # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
                for _ in filter(lambda node: NodeText.satisfies(node, "ROOT"), ChildOf.search_node_iterator(s)):
                    for vp in filter(
                        lambda node: NodeText.satisfies(node, "VP"),
                        HasLeftmostChild.search_node_iterator(s),
                    ):
                        for _ in filter(
                            lambda node: NodeText.satisfies(node, "VB"),
                            ImmediatelyHeadedBy.search_node_iterator(vp),
                        ):
                            yield candidate
                # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                for _ in filter(
                    lambda node: NodeText.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                    ImmediatelyHeadedBy.search_node_iterator(s),
                ):
                    yield candidate
                # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                for vp in filter(lambda node: NodeText.satisfies(node, "VP"), ParentOf.search_node_iterator(s)):
                    # Branch 3.1: VP <# MD|VBP|VBZ|VBD
                    for _ in filter(
                        lambda node: NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                        ImmediatelyHeadedBy.search_node_iterator(vp),
                    ):
                        yield candidate
                    # Branch 3.2: VP < CC < (VP <# MD|VBP|VBZ|VBD)
                    for _ in filter(
                        lambda node: NodeText.satisfies(node, "CC"),
                        ParentOf.search_node_iterator(vp),
                    ):
                        for vp2 in filter(
                            lambda node: NodeText.satisfies(node, "VP"),
                            ParentOf.search_node_iterator(vp),
                        ):
                            for _ in filter(
                                lambda node: NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                ImmediatelyHeadedBy.search_node_iterator(vp2),
                            ):
                                yield candidate


class CT(AbstractSearcher):
    @classmethod
    def condition_one_helper(cls, t: Tree) -> Generator[Tree, None, None]:
        # Condition 1: S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]]
        # Branch 1.1: S|SBARQ|SINV|SQ > ROOT
        # Branch 1.2: S|SBARQ|SINV|SQ $-- S|SBARQ|SINV|SQ !>> SBAR|VP
        for _ in filter(lambda node: NodeText.satisfies(node, "ROOT"), ChildOf.search_node_iterator(t)):
            yield t
        for _ in filter(
            lambda node: NodeText.in_(node, ("S", "SBARQ", "SINV", "SQ")),
            RightSisterOf.search_node_iterator(t),
        ):
            if not any(NodeText.in_(node, ("SBAR", "VP")) for node in DominatedBy.search_node_iterator(t)):
                yield t

    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))
        """
        for candidate in t.visit():
            if not NodeText.in_(candidate, ("S", "SBARQ", "SINV", "SQ")):
                continue
            for _ in cls.condition_one_helper(candidate):
                # Condition 2: S|SBARQ|SINV|SQ << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))
                for sbar in filter(
                    lambda node: NodeText.satisfies(node, "SBAR"),
                    Dominates.search_node_iterator(candidate),
                ):
                    for s in filter(
                        lambda node: NodeText.in_(node, ("S", "SINV", "SQ")),
                        ParentOf.search_node_iterator(sbar),
                    ):
                        # Branch 2.1: S|SINV|SQ > ROOT <, (VP <# VB)
                        for _ in filter(
                            lambda node: NodeText.satisfies(node, "ROOT"),
                            ChildOf.search_node_iterator(s),
                        ):
                            for vp in filter(
                                lambda node: NodeText.satisfies(node, "VP"),
                                HasLeftmostChild.search_node_iterator(s),
                            ):
                                for _ in filter(
                                    lambda node: NodeText.satisfies(node, "VB"),
                                    ImmediatelyHeadedBy.search_node_iterator(vp),
                                ):
                                    yield candidate
                        # Branch 2.2: S|SINV|SQ <# MD|VBZ|VBP|VBD
                        for _ in filter(
                            lambda node: NodeText.in_(node, ("MD", "VBZ", "VBP", "VBD")),
                            ImmediatelyHeadedBy.search_node_iterator(s),
                        ):
                            yield candidate
                        # Branch 2.3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
                        for vp in filter(
                            lambda node: NodeText.satisfies(node, "VP"),
                            ParentOf.search_node_iterator(s),
                        ):
                            # Branch 2.3.1: VP <# MD|VBP|VBZ|VBD
                            for _ in filter(
                                lambda node: NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                ImmediatelyHeadedBy.search_node_iterator(vp),
                            ):
                                yield candidate
                            # Branch 2.3.2: VP < CC < (VP <# MD|VBP|VBZ|VBD)
                            for _ in filter(
                                lambda node: NodeText.satisfies(node, "CC"),
                                ParentOf.search_node_iterator(vp),
                            ):
                                for vp2 in filter(
                                    lambda node: NodeText.satisfies(node, "VP"),
                                    ParentOf.search_node_iterator(vp),
                                ):
                                    for _ in filter(
                                        lambda node: NodeText.in_(node, ("MD", "VBP", "VBZ", "VBD")),
                                        ImmediatelyHeadedBy.search_node_iterator(vp2),
                                    ):
                                        yield candidate


class CP(AbstractSearcher):
    @classmethod
    def search_node_iterator(cls, t: Tree) -> Generator[Tree, None, None]:
        """
        ADJP|ADVP|NP|VP < CC
        """
        for candidate in t.visit():
            if not NodeText.in_(candidate, ("ADJP", "ADVP", "NP", "VP")):
                continue
            for _ in filter(
                lambda node: NodeText.satisfies(node, "CC"),
                ParentOf.search_node_iterator(candidate),
            ):
                yield candidate
