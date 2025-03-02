#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections.abc import Generator, Iterator
from itertools import chain as _chain
from typing import TYPE_CHECKING, Optional

from typing_extensions import override

from ..ns_tregex.collins_head_finder import CollinsHeadFinder

if TYPE_CHECKING:
    from ..ns_tregex.head_finder import HeadFinder
    from ..ns_tregex.node_descriptions import NodeDescriptions
    from ..ns_tregex.tree import Tree

# reference: https://nlp.stanford.edu/nlp/javadoc/javanlp-3.5.0/edu/stanford/nlp/trees/tregex/TregexPattern.html
# translated from https://github.com/stanfordnlp/CoreNLP/blob/main/src/edu/stanford/nlp/trees/tregex/Relation.java
# last modified at Apr 3, 2022 (https://github.com/stanfordnlp/CoreNLP/commits/main/src/edu/stanford/nlp/trees/tregex/Relation.java)

# ------------------------------------------------------------------------------

# TODO ROOT subclass


class Relation(ABC):
    @classmethod
    @abstractmethod
    def satisfies(cls, *args, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def search_node_iterator(cls, *args, **kwargs) -> Generator["Tree", None, None]:
        raise NotImplementedError


class Dominates(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        """
        `t1` and `t2` should be part of the same tree
        """
        while t2.parent is not None:
            if t2.parent is t1:
                return True
            else:
                t2 = t2.parent
        return False

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        iterator = iter(t.children)
        while (node := next(iterator, None)) is not None:
            yield node
            if not node.is_leaf():
                iterator = _chain(node.children, iterator)


class DominatedBy(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return Dominates.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        while parent_ is not None:
            yield parent_
            parent_ = parent_.parent


class OnlyChildOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        those_children = t2.children
        return len(those_children) == 1 and those_children[0] is t1

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None and parent_.num_children() == 1:
            yield parent_


class HasOnlyChild(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return OnlyChildOf.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        if not t.is_leaf() and t.num_children() == 1:
            yield t.children[0]


class LastChildOfParent(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        those_children = t2.children
        return len(those_children) > 0 and those_children[-1] is t1

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None and parent_.last_child() is t:
            yield parent_


class ParentOfLastChild(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return LastChildOfParent.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid = t.last_child()
        if kid is not None:
            yield kid


class LeftmostChildOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        those_children = t2.children
        return len(those_children) > 0 and those_children[0] is t1

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None and parent_.first_child() is t:
            yield parent_


class HasLeftmostChild(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return LeftmostChildOf.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid = t.first_child()
        if kid is not None:
            yield kid


class HasRightmostDescendant(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1.is_leaf():
            return False
        lastChild = t1.children[-1]
        return lastChild is t2 or HasRightmostDescendant.satisfies(lastChild, t2)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid = t.last_child()
        while kid is not None:
            yield kid
            kid = kid.last_child()


class RightmostDescendantOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return HasRightmostDescendant.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current = t
        parent_ = t.parent
        while parent_ is not None and parent_.last_child() is current:
            yield parent_
            current = parent_
            parent_ = parent_.parent


class HasLeftmostDescendant(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1.is_leaf():
            return False
        first_child = t1.children[0]
        return first_child is t2 or HasLeftmostDescendant.satisfies(first_child, t2)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid: Tree | None = t.first_child()
        while kid is not None:
            yield kid
            kid = kid.first_child()


class LeftmostDescendantOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return HasLeftmostDescendant.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current = t
        parent_ = t.parent
        while parent_ is not None and parent_.first_child() is current:
            yield parent_
            current = parent_
            parent_ = parent_.parent


class LeftSisterOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        # t1 is t2 or t1 is root
        if t1 is t2 or t1.parent is None:
            return False

        sisters = t1.parent.children
        for i in range(len(sisters) - 1, 0, -1):  # from sisters[-1] to sisters[1]
            if sisters[i] is t1:
                return False
            if sisters[i] is t2:
                return True
        return False

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for child in reversed(parent_.children):
                # https://stackoverflow.com/questions/16465046/why-is-reversing-a-list-with-slicing-slower-than-reverse-iterator
                if child is t:
                    break
                yield child


class RightSisterOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return LeftSisterOf.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for child in parent_.children:
                if child is t:
                    break
                yield child


class ImmediateLeftSisterOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        # t1 is t2 or t1 is root
        if t1 is t2 or t1.parent is None:
            return False

        sisters = t1.parent.children
        for i in range(len(sisters) - 1, 0, -1):  # from sisters[-1] to sisters[1]
            if sisters[i] is t1:
                return False
            if sisters[i] is t2:
                return sisters[i - 1] is t1
        return False

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for i, child in enumerate(parent_.children):  # noqa: B007
                if child is t:
                    break
            if i + 1 < parent_.num_children():  # type:ignore
                yield parent_.children[i + 1]  # type:ignore


class ImmediateRightSisterOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return ImmediateLeftSisterOf.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for i, child in enumerate(parent_.children):  # noqa: B007
                if child is t:
                    break
            if i > 0:  # type:ignore
                yield parent_.children[i - 1]  # type:ignore


class ParentOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t2.parent is t1

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        yield from t.children


class ChildOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return ParentOf.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            yield parent_


class SisterOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1 is t2 or t1.parent is None:
            return False
        parent_ = t1.parent
        return ParentOf.satisfies(parent_, t2)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for sister in parent_.children:
                if sister is t:
                    continue
                yield sister


class EQUALS(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1 is t2

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        yield t


class ParentEquals(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1 is t2:
            return True
        return ParentOf.satisfies(t1, t2)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        yield t
        yield from t.children


class UnaryPathAncestorOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1.is_leaf() or t1.num_children() > 1:
            return False
        only_child = t1.children[0]
        if only_child is t2:
            return True
        else:
            return UnaryPathAncestorOf.satisfies(only_child, t2)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        next = t
        while next.num_children() == 1:
            kid = next.children[0]
            yield kid
            next = kid


class UnaryPathDescedantOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return UnaryPathAncestorOf.satisfies(t2, t1)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        while parent_ is not None and parent_.num_children() == 1:
            yield parent_
            parent_ = parent_.parent


class HEADS(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", headFinder: Optional["HeadFinder"] = None) -> bool:
        if t2.is_leaf():
            return False
        elif t2.is_preterminal():
            return t2.first_child() is t1
        else:
            if headFinder is None:
                headFinder = cls.hf
            head = headFinder.determineHead(t2)
            if head is None:
                return False
            elif head is t1:
                return True
            else:
                return cls.satisfies(t1, head, headFinder)

    @classmethod
    @override
    def search_node_iterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        if headFinder is None:
            headFinder = cls.hf
        parent_ = t.parent
        while parent_ is not None and headFinder.determineHead(parent_) is t:
            yield parent_
            parent_ = parent_.parent


class HeadedBy(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", hf: Optional["HeadFinder"] = None) -> bool:
        return HEADS.satisfies(t2, t1, hf)

    @classmethod
    @override
    def search_node_iterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        if headFinder is None:
            headFinder = cls.hf
        if not t.is_leaf():
            head = headFinder.determineHead(t)
            while head is not None:
                yield head
                head = headFinder.determineHead(head)


class ImmediatelyHeads(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", headFinder: Optional["HeadFinder"] = None) -> bool:
        if headFinder is None:
            headFinder = cls.hf
        return headFinder.determineHead(t2) is t1

    @classmethod
    @override
    def search_node_iterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:  # if t is not root
            if headFinder is None:
                headFinder = cls.hf
            if headFinder.determineHead(parent_) is t:
                yield parent_


class ImmediatelyHeadedBy(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", headFinder: Optional["HeadFinder"] = None) -> bool:
        return ImmediatelyHeads.satisfies(t2, t1, headFinder)

    @classmethod
    @override
    def search_node_iterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        if t.is_leaf():
            return
        if headFinder is None:
            headFinder = cls.hf
        head = headFinder.determineHead(t)
        if head is not None:
            yield head


class PRECEDES(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1.right_edge() <= t2.left_edge()

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        searchStack: list[Tree] = []
        current: Tree | None = t
        parent_: Tree | None = t.parent
        while parent_ is not None:
            for kid in reversed(parent_.children):
                if kid is current:
                    break
                searchStack.append(kid)
            current = parent_
            parent_ = parent_.parent
        while searchStack:
            next = searchStack.pop()
            yield next
            searchStack.extend(reversed(next.children))


class ImmediatelyPrecedes(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1.right_edge() == t2.left_edge()

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current: Tree | None = None
        parent_: Tree | None = t
        while True:
            current = parent_  # type: ignore
            parent_ = parent_.parent  # type: ignore
            if parent_ is None:
                return
            if parent_.last_child() is not current:
                break
        for i, kid in enumerate(parent_.children):  # noqa: B007
            if kid is current:
                break
        # Use i+1 won't cause IndexError because current is not the last child
        next = parent_.children[i + 1]  # type:ignore
        while True:
            yield next  # type:ignore
            if next.is_leaf():  # type:ignore
                break
            next = next.first_child()  # type:ignore


class FOLLOWS(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t2.right_edge() <= t1.left_edge()

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        searchStack: list[Tree] = []
        current: Tree | None = t
        parent_: Tree | None = t.parent
        while parent_ is not None:
            for kid in parent_.children:
                if kid is current:
                    break
                searchStack.append(kid)
            current = parent_
            parent_ = parent_.parent
        while searchStack:
            next = searchStack.pop()
            yield next
            searchStack.extend(reversed(next.children))


class ImmediatelyFollows(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t2.right_edge() == t1.left_edge()

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current: Tree | None = None
        parent_: Tree | None = t
        while True:
            current = parent_
            parent_ = parent_.parent  # type: ignore
            if parent_ is None:
                return
            if parent_.first_child() is not current:
                break
        for i, kid in enumerate(parent_.children):  # noqa: B007
            if kid is current:
                break
        # Use i-1 won't cause IndexError because current is not the first child
        next = parent_.children[i - 1]  # type:ignore
        while True:
            yield next  # type:ignore
            if next.is_leaf():  # type:ignore
                break
            next = next.last_child()  # type:ignore


class AncestorOfLeaf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1 is not t2 and t2.is_leaf() and Dominates.satisfies(t1, t2)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        iterator = iter(t.children)
        while (node := next(iterator, None)) is not None:
            if node.is_leaf():
                yield node
            else:
                iterator = _chain(node.children, iterator)


class UnbrokenCategoryDominates(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        # TODO passing in rel_arg is expansive, may be passing in node_descriptions is better?
        for kid in t1.children:
            if kid is t2:
                return True
            else:
                if descs.satisfy(kid) and UnbrokenCategoryDominates.satisfies(kid, t2, descs):
                    return True
        return False

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        # TODO might need to implement a TregexMatcher class like java tregex
        # https://github.com/stanfordnlp/CoreNLP/blob/f8838d2639589f684cbaa58964cb29db5f23df7f/src/edu/stanford/nlp/trees/tregex/Relation.java#L1525
        iterator = iter(t.children)
        while (node := next(iterator, None)) is not None:
            # chain of length zero
            yield node
            # chain of length longer than 0
            if descs.satisfy(node):
                iterator = _chain(node.children, iterator)


class UnbrokenCategoryIsDominatedBy(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        return UnbrokenCategoryDominates.satisfies(t2, t1, descs)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        parent_ = t.parent
        while True:
            if parent_ is None:
                break
            yield parent_
            if not descs.satisfy(parent_):
                break
            parent_ = parent_.parent


class UnbrokenCategoryPrecedes(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        parent_ = t1.parent
        if parent_ is None:  # if t1 is root
            return False
        i = t1.get_sister_index()
        while i == (parent_.num_children() - 1) and parent_.parent is not None:
            t1 = parent_
            parent_ = parent_.parent
            i = t1.get_sister_index()

        # ensure i >= 0 because Tree.get_sister_index() might return -1
        if i >= 0 and (i + 1) < parent_.num_children():
            immediate_follower = parent_.children[i + 1]
        else:
            return False

        if immediate_follower is t2:
            return True
        else:
            if descs.satisfy(immediate_follower) and UnbrokenCategoryPrecedes.satisfies(
                immediate_follower, t2, descs
            ):
                return True
        return False

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        iterator: Iterator = ImmediatelyPrecedes.search_node_iterator(t)
        while (node := next(iterator, None)) is not None:
            yield node
            if descs.satisfy(node):
                iterator = _chain(ImmediatelyPrecedes.search_node_iterator(node), iterator)


class UnbrokenCategoryFollows(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        return UnbrokenCategoryPrecedes.satisfies(t2, t1, descs)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        iterator: Iterator = ImmediatelyFollows.search_node_iterator(t)
        while (node := next(iterator, None)) is not None:
            yield node
            if descs.satisfy(node):
                iterator = _chain(ImmediatelyFollows.search_node_iterator(node), iterator)


class PatternSplitter(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return True

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        root = t.get_root()
        return root.visit()


class IthChildOf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", child_num: int) -> bool:
        if child_num == 0:
            raise ValueError("Error -- no such thing as zeroth child!")

        kids = t2.children
        if abs(child_num) > len(kids):
            return False
        if child_num > 0 and kids[child_num - 1] is t1:
            return True
        if child_num < 0 and kids[len(kids) + child_num] is t1:  # noqa: SIM103
            return True

        return False

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree", child_num: int) -> Generator["Tree", None, None]:
        if child_num == 0:
            raise ValueError("Error -- no such thing as zeroth child!")
        parent_ = t.parent
        if parent_ is None:
            return
        if abs(child_num) > parent_.num_children():
            return
        kids = parent_.children
        if (child_num > 0 and kids[child_num - 1] is t) or (child_num < 0 and kids[child_num] is t):
            yield parent_


class HasIthChild(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", child_num: int) -> bool:
        return IthChildOf.satisfies(t2, t1, child_num)

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree", child_num: int) -> Generator["Tree", None, None]:
        if child_num == 0:
            raise ValueError("Error -- no such thing as zeroth child!")
        if t.is_leaf():
            return
        if abs(child_num) > t.num_children():
            return
        if child_num > 0:
            yield t.children[child_num - 1]
        else:
            yield t.children[child_num]


class AncestorOfIthLeaf(Relation):
    @classmethod
    @override
    def satisfies(cls, t1: "Tree", t2: "Tree", leaf_num: int) -> bool:
        if leaf_num == 0:
            raise ValueError("Error -- no such thing as zeroth leaf!")

        if t1 is t2 or not t2.is_leaf():
            return False

        # this is kind of lazy if it somehow became a performance limitation, a
        # recursive search would be faster
        leaves = t1.get_leaves()
        if len(leaves) < abs(leaf_num):
            return False
        index = leaf_num - 1 if leaf_num > 0 else len(leaves) + leaf_num
        return leaves[index] is t2

    @classmethod
    @override
    def search_node_iterator(cls, t: "Tree", leaf_num: int) -> Generator["Tree", None, None]:
        if leaf_num == 0:
            raise ValueError("Error -- no such thing as zeroth leaf!")
        if t.is_leaf():
            return
        leaves = t.get_leaves()
        if len(leaves) >= abs(leaf_num):
            if leaf_num > 0:
                yield leaves[leaf_num - 1]
            else:
                yield leaves[leaf_num]


# ------------------------------------------------------------------------------
# RelationData


class AbstractRelationData(ABC):
    def __init__(self, strins_repr: str, op: Relation):
        self.op = op
        self.strins_repr = strins_repr

    def __repr__(self) -> str:
        return self.strins_repr

    def set_strins_repr(self, s: str) -> None:
        self.strins_repr = s

    @abstractmethod
    def search_node_iterator(self, this_node: "Tree"):
        raise NotImplementedError()

    @abstractmethod
    def satisfies(self, this_node: "Tree", that_node: "Tree"):
        raise NotImplementedError()


class RelationData(AbstractRelationData):
    def __init__(self, strins_repr: str, op: Relation) -> None:
        super().__init__(strins_repr, op)

    @override
    def search_node_iterator(self, this_node: "Tree") -> Generator["Tree", None, None]:
        return self.op.search_node_iterator(this_node)

    @override
    def satisfies(self, this_node: "Tree", that_node: "Tree") -> bool:
        return self.op.satisfies(this_node, that_node)


class RelationWithStrArgData(AbstractRelationData):
    def __init__(
        self,
        strins_repr: str,
        op: Relation,
        *,
        arg: "NodeDescriptions",
    ) -> None:
        super().__init__(strins_repr, op)
        self.arg = arg

    @override
    def search_node_iterator(self, this_node: "Tree") -> Generator["Tree", None, None]:
        return self.op.search_node_iterator(this_node, self.arg)

    @override
    def satisfies(self, this_node: "Tree", that_node: "Tree") -> bool:
        return self.op.satisfies(this_node, that_node, self.arg)


class RelationWithNumArgData(AbstractRelationData):
    def __init__(
        self,
        strins_repr: str,
        op: Relation,
        *,
        arg: int,
    ) -> None:
        super().__init__(strins_repr, op)
        self.arg = arg

    @override
    def search_node_iterator(self, this_node: "Tree") -> Generator["Tree", None, None]:
        return self.op.search_node_iterator(this_node, self.arg)

    @override
    def satisfies(self, this_node: "Tree", that_node: "Tree") -> bool:
        return self.op.satisfies(this_node, that_node, self.arg)


class MultiRelationData(RelationWithNumArgData):
    def __init__(
        self,
        strins_repr: str,
        op: Relation,
        *,
        arg: int,
    ) -> None:
        super().__init__(strins_repr, op, arg=arg)
