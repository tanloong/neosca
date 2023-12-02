#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, List, Optional

from neosca_gui.tregex.collins_head_finder import CollinsHeadFinder

if TYPE_CHECKING:
    from neosca_gui.tregex.head_finder import HeadFinder
    from neosca_gui.tregex.node_descriptions import NodeDescriptions
    from neosca_gui.tregex.tree import Tree

# reference: https://nlp.stanford.edu/nlp/javadoc/javanlp-3.5.0/edu/stanford/nlp/trees/tregex/TregexPattern.html
# translated from https://github.com/stanfordnlp/CoreNLP/blob/main/src/edu/stanford/nlp/trees/tregex/Relation.java
# last modified at Apr 3, 2022 (https://github.com/stanfordnlp/CoreNLP/commits/main/src/edu/stanford/nlp/trees/tregex/Relation.java)

# ------------------------------------------------------------------------------

# TODO ROOT subclass


class Relation:
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", arg=None) -> bool:
        raise NotImplementedError

    @classmethod
    def searchNodeIterator(cls, t: "Tree", arg=None) -> Generator["Tree", None, None]:
        raise NotImplementedError


class DOMINATES(Relation):
    @classmethod
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
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        for child in t.children:
            yield child
            yield from cls.searchNodeIterator(child)


class DOMINATED_BY(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return DOMINATES.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        while parent_ is not None:
            yield parent_
            parent_ = parent_.parent


class ONLY_CHILD_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        those_children = t2.children
        return len(those_children) == 1 and those_children[0] is t1

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None and parent_.numChildren() == 1:
            yield parent_


class HAS_ONLY_CHILD(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return ONLY_CHILD_OF.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        if not t.isLeaf() and t.numChildren() == 1:
            yield t.children[0]


class LAST_CHILD_OF_PARENT(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        those_children = t2.children
        return len(those_children) > 0 and those_children[-1] is t1

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None and parent_.lastChild() is t:
            yield parent_


class PARENT_OF_LAST_CHILD(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return LAST_CHILD_OF_PARENT.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid = t.lastChild()
        if kid is not None:
            yield kid


class LEFTMOST_CHILD_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        those_children = t2.children
        return len(those_children) > 0 and those_children[0] is t1

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None and parent_.firstChild() is t:
            yield parent_


class HAS_LEFTMOST_CHILD(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return LEFTMOST_CHILD_OF.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid = t.firstChild()
        if kid is not None:
            yield kid


class HAS_RIGHTMOST_DESCENDANT(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1.isLeaf():
            return False
        lastChild = t1.children[-1]
        return lastChild is t2 or HAS_RIGHTMOST_DESCENDANT.satisfies(lastChild, t2)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid = t.lastChild()
        while kid is not None:
            yield kid
            kid = kid.lastChild()


class RIGHTMOST_DESCENDANT_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return HAS_RIGHTMOST_DESCENDANT.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current = t
        parent_ = t.parent
        while parent_ is not None and parent_.lastChild() is current:
            yield parent_
            current = parent_
            parent_ = parent_.parent


class HAS_LEFTMOST_DESCENDANT(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1.isLeaf():
            return False
        first_child = t1.children[0]
        return first_child is t2 or HAS_LEFTMOST_DESCENDANT.satisfies(first_child, t2)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        kid: Optional["Tree"] = t.firstChild()
        while kid is not None:
            yield kid
            kid = kid.firstChild()


class LEFTMOST_DESCENDANT_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return HAS_LEFTMOST_DESCENDANT.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current = t
        parent_ = t.parent
        while parent_ is not None and parent_.firstChild() is current:
            yield parent_
            current = parent_
            parent_ = parent_.parent


class LEFT_SISTER_OF(Relation):
    @classmethod
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
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for child in reversed(parent_.children):
                # https://stackoverflow.com/questions/16465046/why-is-reversing-a-list-with-slicing-slower-than-reverse-iterator
                if child is t:
                    break
                yield child


class RIGHT_SISTER_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return LEFT_SISTER_OF.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for child in parent_.children:
                if child is t:
                    break
                yield child


class IMMEDIATE_LEFT_SISTER_OF(Relation):
    @classmethod
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
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for i, child in enumerate(parent_.children):
                if child is t:
                    break
            if i + 1 < parent_.numChildren():
                yield parent_.children[i + 1]


class IMMEDIATE_RIGHT_SISTER_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return IMMEDIATE_LEFT_SISTER_OF.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for i, child in enumerate(parent_.children):
                if child is t:
                    break
            if i > 0:
                yield parent_.children[i - 1]


class PARENT_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t2.parent is t1

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        yield from t.children


class CHILD_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return PARENT_OF.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            yield parent_


class SISTER_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1 is t2 or t1.parent is None:
            return False
        parent_ = t1.parent
        return PARENT_OF.satisfies(parent_, t2)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:
            for sister in parent_.children:
                if sister is t:
                    continue
                yield sister


class EQUALS(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1 is t2

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        yield t


class PARENT_EQUALS(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1 is t2:
            return True
        return PARENT_OF.satisfies(t1, t2)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        yield t
        yield from t.children


class UNARY_PATH_ANCESTOR_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        if t1.isLeaf() or t1.numChildren() > 1:
            return False
        only_child = t1.children[0]
        if only_child is t2:
            return True
        else:
            return UNARY_PATH_ANCESTOR_OF.satisfies(only_child, t2)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        next = t
        while next.numChildren() == 1:
            kid = next.children[0]
            yield kid
            next = kid


class UNARY_PATH_DESCEDANT_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return UNARY_PATH_ANCESTOR_OF.satisfies(t2, t1)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        parent_ = t.parent
        while parent_ is not None and parent_.numChildren() == 1:
            yield parent_
            parent_ = parent_.parent


class HEADS(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", headFinder: Optional["HeadFinder"] = None) -> bool:
        if t2.isLeaf():
            return False
        elif t2.is_pre_terminal:
            return t2.firstChild() is t1
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
    def searchNodeIterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        if headFinder is None:
            headFinder = cls.hf
        parent_ = t.parent
        while parent_ is not None and headFinder.determineHead(parent_) is t:
            yield parent_
            parent_ = parent_.parent


class HEADED_BY(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", hf: Optional["HeadFinder"] = None) -> bool:
        return HEADS.satisfies(t2, t1, hf)

    @classmethod
    def searchNodeIterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        if headFinder is None:
            headFinder = cls.hf
        if not t.isLeaf():
            head = headFinder.determineHead(t)
            while head is not None:
                yield head
                head = headFinder.determineHead(head)


class IMMEDIATELY_HEADS(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", headFinder: Optional["HeadFinder"] = None) -> bool:
        if headFinder is None:
            headFinder = cls.hf
        return headFinder.determineHead(t2) is t1

    @classmethod
    def searchNodeIterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        parent_ = t.parent
        if parent_ is not None:  # if t is not root
            if headFinder is None:
                headFinder = cls.hf
            if headFinder.determineHead(parent_) is t:
                yield parent_


class IMMEDIATELY_HEADED_BY(Relation):
    hf = CollinsHeadFinder()

    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", headFinder: Optional["HeadFinder"] = None) -> bool:
        return IMMEDIATELY_HEADS.satisfies(t2, t1, headFinder)

    @classmethod
    def searchNodeIterator(
        cls, t: "Tree", headFinder: Optional["HeadFinder"] = None
    ) -> Generator["Tree", None, None]:
        if t.isLeaf():
            return
        if headFinder is None:
            headFinder = cls.hf
        head = headFinder.determineHead(t)
        if head is not None:
            yield head


class PRECEDES(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1.rightEdge() <= t2.leftEdge()

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        searchStack: List["Tree"] = []
        current: Optional["Tree"] = t
        parent_: Optional["Tree"] = t.parent
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


class IMMEDIATELY_PRECEDES(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1.rightEdge() == t2.leftEdge()

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current: Optional["Tree"] = None
        parent_: Optional["Tree"] = t
        while True:
            current = parent_
            parent_ = parent_.parent
            if parent_ is None:
                return
            if parent_.lastChild() is not current:
                break
        for i, kid in enumerate(parent_.children):
            if kid is current:
                break
        # Use i+1 won't cause IndexError because current is not the last child
        next = parent_.children[i + 1]
        while True:
            yield next
            if next.isLeaf():
                break
            next = next.firstChild()


class FOLLOWS(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t2.rightEdge() <= t1.leftEdge()

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        searchStack: List["Tree"] = []
        current: Optional["Tree"] = t
        parent_: Optional["Tree"] = t.parent
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


class IMMEDIATELY_FOLLOWS(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t2.rightEdge() == t1.leftEdge()

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        current: Optional["Tree"] = None
        parent_: Optional["Tree"] = t
        while True:
            current = parent_
            parent_ = parent_.parent
            if parent_ is None:
                return
            if parent_.firstChild() is not current:
                break
        for i, kid in enumerate(parent_.children):
            if kid is current:
                break
        # Use i-1 won't cause IndexError because current is not the first child
        next = parent_.children[i - 1]
        while True:
            yield next
            if next.isLeaf():
                break
            next = next.lastChild()


class ANCESTOR_OF_LEAF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return t1 is not t2 and t2.isLeaf() and DOMINATES.satisfies(t1, t2)

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        for kid in t.children:
            if kid.isLeaf():
                yield kid
                continue
            # If t is leaf, then t.children would be an empty list
            yield from cls.searchNodeIterator(kid)


class UNBROKEN_CATEGORY_DOMINATES(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        # TODO passing in rel_arg is expansive, may be passing in node_descriptions is better?
        for kid in t1.children:
            if kid is t2:
                return True
            else:
                if descs.satisfy(kid) and UNBROKEN_CATEGORY_DOMINATES.satisfies(kid, t2, descs):
                    return True
        return False

    @classmethod
    def searchNodeIterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        # TODO might need to implement a TregexMatcher class like java tregex
        # https://github.com/stanfordnlp/CoreNLP/blob/f8838d2639589f684cbaa58964cb29db5f23df7f/src/edu/stanford/nlp/trees/tregex/Relation.java#L1525
        for kid in t.children:
            # chain of length zero
            yield kid
            # chain of length longer than 0
            if descs.satisfy(kid):
                yield from cls.searchNodeIterator(kid, descs)


class UNBROKEN_CATEGORY_IS_DOMINATED_BY(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        return UNBROKEN_CATEGORY_DOMINATES.satisfies(t2, t1, descs)

    @classmethod
    def searchNodeIterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        parent_ = t.parent
        while True:
            if parent_ is None:
                break
            yield parent_
            if not descs.satisfy(parent_):
                break
            parent_ = parent_.parent


class UNBROKEN_CATEGORY_PRECEDES(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        parent_ = t1.parent
        if parent_ is None:  # if t1 is root
            return False
        i = t1.get_sister_index()
        while i == (parent_.numChildren() - 1) and parent_.parent is not None:
            t1 = parent_
            parent_ = parent_.parent
            i = t1.get_sister_index()

        # ensure i >= 0 because Tree.get_sister_index() might return -1
        if i >= 0 and (i + 1) < parent_.numChildren():
            immediate_follower = parent_.children[i + 1]
        else:
            return False

        if immediate_follower is t2:
            return True
        else:
            if descs.satisfy(immediate_follower) and UNBROKEN_CATEGORY_PRECEDES.satisfies(
                immediate_follower, t2, descs
            ):
                return True
        return False

    @classmethod
    def searchNodeIterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        for immediate_follower in IMMEDIATELY_PRECEDES.searchNodeIterator(t):
            yield immediate_follower
            if descs.satisfy(immediate_follower):
                yield from cls.searchNodeIterator(immediate_follower, descs)


class UNBROKEN_CATEGORY_FOLLOWS(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", descs: "NodeDescriptions") -> bool:
        return UNBROKEN_CATEGORY_PRECEDES.satisfies(t2, t1, descs)

    @classmethod
    def searchNodeIterator(cls, t: "Tree", descs: "NodeDescriptions") -> Generator["Tree", None, None]:
        for immediate_precedent in IMMEDIATELY_FOLLOWS.searchNodeIterator(t):
            yield immediate_precedent
            if descs.satisfy(immediate_precedent):
                yield from cls.searchNodeIterator(immediate_precedent, descs)


class PATTERN_SPLITTER(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree") -> bool:
        return True

    @classmethod
    def searchNodeIterator(cls, t: "Tree") -> Generator["Tree", None, None]:
        root = t.getRoot()
        return root.preorder_iter()


class ITH_CHILD_OF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", child_num: int) -> bool:
        if child_num == 0:
            raise ValueError("Error -- no such thing as zeroth child!")

        kids = t2.children
        if abs(child_num) > len(kids):
            return False
        if child_num > 0 and kids[child_num - 1] is t1:
            return True
        if child_num < 0 and kids[len(kids) + child_num] is t1:
            return True

        return False

    @classmethod
    def searchNodeIterator(cls, t: "Tree", child_num: int) -> Generator["Tree", None, None]:
        if child_num == 0:
            raise ValueError("Error -- no such thing as zeroth child!")
        parent_ = t.parent
        if parent_ is None:
            return
        if abs(child_num) > parent_.numChildren():
            return
        kids = parent_.children
        if (child_num > 0 and kids[child_num - 1] is t) or (child_num < 0 and kids[child_num] is t):
            yield parent_


class HAS_ITH_CHILD(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", child_num: int) -> bool:
        return ITH_CHILD_OF.satisfies(t2, t1, child_num)

    @classmethod
    def searchNodeIterator(cls, t: "Tree", child_num: int) -> Generator["Tree", None, None]:
        if child_num == 0:
            raise ValueError("Error -- no such thing as zeroth child!")
        if t.isLeaf():
            return
        if abs(child_num) > t.numChildren():
            return
        if child_num > 0:
            yield t.children[child_num - 1]
        else:
            yield t.children[child_num]


class ANCESTOR_OF_ITH_LEAF(Relation):
    @classmethod
    def satisfies(cls, t1: "Tree", t2: "Tree", leaf_num: int) -> bool:
        if leaf_num == 0:
            raise ValueError("Error -- no such thing as zeroth leaf!")

        if t1 is t2 or not t2.isLeaf():
            return False

        # this is kind of lazy if it somehow became a performance limitation, a
        # recursive search would be faster
        leaves = t1.getLeaves()
        if len(leaves) < abs(leaf_num):
            return False
        if leaf_num > 0:
            index = leaf_num - 1
        else:
            # eg, leafNum == -1 means we check leaves.size() - 1
            index = len(leaves) + leaf_num
        return leaves[index] is t2

    @classmethod
    def searchNodeIterator(cls, t: "Tree", leaf_num: int) -> Generator["Tree", None, None]:
        if leaf_num == 0:
            raise ValueError("Error -- no such thing as zeroth leaf!")
        if t.isLeaf():
            return
        leaves = t.getLeaves()
        if len(leaves) >= abs(leaf_num):
            if leaf_num > 0:
                yield leaves[leaf_num - 1]
            else:
                yield leaves[leaf_num]


# ------------------------------------------------------------------------------
# RelationData


class AbstractRelationData(ABC):
    def __init__(self, string_repr: str, op: Relation):
        self.op = op
        self.string_repr = string_repr

    def __repr__(self) -> str:
        return self.string_repr

    def set_string_repr(self, s: str) -> None:
        self.string_repr = s

    @abstractmethod
    def searchNodeIterator(self, this_node: "Tree"):
        raise NotImplementedError()

    @abstractmethod
    def satisfies(self, this_node: "Tree", that_node: "Tree"):
        raise NotImplementedError()


class RelationData(AbstractRelationData):
    def __init__(self, string_repr: str, op: Relation) -> None:
        super().__init__(string_repr, op)

    def searchNodeIterator(self, this_node: "Tree") -> Generator["Tree", None, None]:
        return self.op.searchNodeIterator(this_node)

    def satisfies(self, this_node: "Tree", that_node: "Tree") -> bool:
        return self.op.satisfies(this_node, that_node)


class RelationWithStrArgData(AbstractRelationData):
    def __init__(
        self,
        string_repr: str,
        op: Relation,
        *,
        arg: "NodeDescriptions",
    ) -> None:
        super().__init__(string_repr, op)
        self.arg = arg

    def searchNodeIterator(self, this_node: "Tree") -> Generator["Tree", None, None]:
        return self.op.searchNodeIterator(this_node, self.arg)

    def satisfies(self, this_node: "Tree", that_node: "Tree") -> bool:
        return self.op.satisfies(this_node, that_node, self.arg)


class RelationWithNumArgData(AbstractRelationData):
    def __init__(
        self,
        string_repr: str,
        op: Relation,
        *,
        arg: int,
    ) -> None:
        super().__init__(string_repr, op)
        self.arg = arg

    def searchNodeIterator(self, this_node: "Tree") -> Generator["Tree", None, None]:
        return self.op.searchNodeIterator(this_node, self.arg)

    def satisfies(self, this_node: "Tree", that_node: "Tree") -> bool:
        return self.op.satisfies(this_node, that_node, self.arg)


class MultiRelationData(RelationWithNumArgData):
    def __init__(
        self,
        string_repr: str,
        op: Relation,
        *,
        arg: int,
    ) -> None:
        super().__init__(string_repr, op, arg=arg)
