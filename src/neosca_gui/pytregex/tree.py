# translated from [CoreNLP](https://github.com/stanfordnlp/CoreNLP/blob/139893242878ecacde79b2ba1d0102b855526610/src/edu/stanford/nlp/trees/Tree.java)

# TODO use camel case to match java tregex's convention

import re
from collections import deque
from typing import TYPE_CHECKING, Deque, Generator, List, Optional, Tuple

from .peekable import peekable

if TYPE_CHECKING:
    from .head_finder import HeadFinder


class Tree:
    def __init__(
        self,
        label: Optional[str] = None,
        children: Optional[List["Tree"]] = None,
        parent: Optional["Tree"] = None,
    ):
        self.set_label(label)
        if children is None:
            self.children = []
        else:
            for child in children:
                child.parent = self  # type:ignore
            self.children = children
        # each subtree has at most one parent
        self.parent = parent

    def __repr__(self):
        if not self.children:  # is leaf
            s = self.label if self.label is not None else ""
        else:
            s = "(%s %s)" % (self.label, " ".join(repr(child) for child in self.children))
        return s

    def __eq__(self, other) -> bool:
        """
        Implements equality for Tree's.  Two Tree objects are equal if they
        have equal labels, the same number of children, and their children
        are pairwise equal. `t1 == t2` does not necessarily mean `t1 is t2`.

        :param other The object to compare with
        :return Whether two things are equal
        """
        if self.__class__ is not other.__class__:
            return False

        label1, label2 = self.label, other.label
        # if one or both of (self, other) has non-None label
        if label1 is not None or label2 is not None:
            if label1 is None or label1 != label2:
                return False

        my_kids = self.children
        their_kids = other.children
        if len(my_kids) != len(their_kids):
            return False
        for i in range(len(my_kids)):
            if my_kids[i] != their_kids[i]:
                return False
        return True

    def __hash__(self) -> int:
        # consider t1's hash different than t2's if they have different id, although t1==t2 might be True
        return id(self)

    def __getitem__(self, index) -> "Tree":
        if isinstance(index, (int, slice)):
            return self.children[index]  # type:ignore
        elif isinstance(index, (list, tuple)):
            if len(index) == 0:
                return self
            elif len(index) == 1:
                return self[index[0]]
            else:
                return self[index[0]][index[1:]]
        else:
            raise TypeError(
                f"{type(self).__name__} indices must be integers, not {type(index).__name__}"
            )

    def __bool__(self) -> bool:
        if self.label is None and not self.children:
            return False
        return True

    def __len__(self) -> int:
        return len(self.children)

    @property
    def basic_category(self) -> Optional[str]:
        if self.label is None:
            return None
        return self.label.split("-")[0]

    def isLeaf(self) -> bool:
        return not self.children

    def numChildren(self) -> int:
        return len(self.children)

    @property
    def is_unary_rewrite(self) -> bool:
        """
        Says whether the current node has only one child. Can be used on an
        arbitrary Tree instance.

        return Whether the node heads a unary rewrite
        """
        return self.numChildren() == 1

    @property
    def is_pre_terminal(self) -> bool:
        """
        A preterminal is defined to be a node with one child which is itself a leaf.
        """
        return self.numChildren() == 1 and self.children[0].isLeaf()

    @property
    def is_pre_pre_terminal(self) -> bool:
        """
        Return whether all the children of this node are preterminals or not.
        A preterminal is
        defined to be a node with one child which is itself a leaf.
        Considered false if the node has no children

        return true if the node is a prepreterminal; false otherwise
        """
        if self.numChildren() == 0:
            return False
        for child in self.children:
            if not child.is_pre_terminal:
                return False
        return True

    @property
    def is_phrasal(self) -> bool:
        """
        Return whether this node is a phrasal node or not.  A phrasal node
        is defined to be a node which is not a leaf or a preterminal.
        Worded positively, this means that it must have two or more children,
        or one child that is not a leaf.

        return True if the node is phrasal; False otherwise
        """
        kids = self.children
        return not (kids is None or len(kids) == 0 or (len(kids) == 1 and kids[0].isLeaf()))

    @property
    def is_binary(self) -> bool:
        """
        Returns whether this node is the root of a possibly binary tree. This
        happens if the tree and all of its descendants are either nodes with
        exactly two children, or are preterminals or leaves.
        """
        if self.isLeaf() or self.is_pre_terminal:
            return True
        kids = self.children
        if len(kids) != 2:
            return False
        return kids[0].is_binary and kids[1].is_binary

    def firstChild(self) -> Optional["Tree"]:
        """
        Returns the first child of a tree, or None if none.

        return The first child
        """
        kids = self.children
        if len(kids) == 0:
            return None
        return kids[0]

    def lastChild(self) -> Optional["Tree"]:
        """
        Returns the last child of a tree, or None if none.

        return The last child
        """
        kids = self.children
        if len(kids) == 0:
            return None
        return kids[-1]

    @property
    def height(self) -> int:
        """
        The height of this tree.  The height of a tree containing no children
        is 1; the height of a tree containing only leaves is 2; and the height
        of any other tree is one plus the maximum of its children's heights.
        """
        if self.isLeaf():
            return 1
        max_height = 0
        for child in self.children:
            max_height = max(max_height, child.height)
        return max_height + 1

    def head_terminal(self, hf: "HeadFinder") -> Optional["Tree"]:
        """
        Returns the tree leaf that is the head of the tree.

        param hf The head-finding algorithm to use
        param parent  The parent of this tree
        return The head tree leaf if any, else null
        """
        if self.isLeaf():
            return self

        head: Optional["Tree"] = hf.determineHead(self)
        if head is not None:
            return head.head_terminal(hf)

        return None

    def yield_(self) -> List[Optional[str]]:
        """
        Gets the yield of the tree.  The Label of all leaf nodes is returned as
        a list ordered by the natural left to right order of the leaves.  Null
        values, if any, are inserted into the list like any other value.

        return a List of the data in the tree's leaves.
        """
        leaves = []
        if self.isLeaf():
            leaves.append(self.label)
        else:
            for child in self.children:
                leaves.extend(child.yield_())
        return leaves

    def tagged_yield_(self, divider: str = "/") -> List[str]:
        """
        Gets the tagged yield of the tree -- that is, get the preterminals as
        well as the terminals.  The Label of all leaf nodes is returned as a
        list ordered by the natural left to right order of the leaves.  Null
        values, if any, are inserted into the list like any other value. This
        has been rewritten to thread, so only one List is used.

        param ty The list in which the tagged yield of the tree will be placed.
        Normally, this will be empty when the routine is called, but if not,
        the new yield is added to the end of the list.
        return a List of the data in the tree's leaves.
        """
        tagged_leaves = []
        if self.is_pre_terminal:
            tagged_leaves.append(f"{self.firstChild().label}{divider}{self.label}")  # type:ignore
        else:
            for child in self.children:
                tagged_leaves.extend(child.tagged_yield_())
        return tagged_leaves

    def leftEdge(self) -> int:
        """
        note: return 0 for the leftmost node
        """
        i = 0

        def left_edge_helper(t: "Tree", t1: "Tree") -> bool:
            nonlocal i
            if t is t1:
                return True
            elif t1.isLeaf():
                j = len(t1.yield_())
                i += j
                return False
            else:
                for kid in t1.children:
                    if left_edge_helper(t, kid):
                        return True
                return False

        if left_edge_helper(self, self.getRoot()):
            return i
        else:
            raise RuntimeError("Tree is not a descendant of root.")

    def rightEdge(self) -> int:
        """
        note: return 1 for the leftmost node
        """
        i = len(self.getRoot().yield_())

        def right_edge_helper(t: "Tree", t1: "Tree") -> bool:
            nonlocal i
            if t is t1:
                return True
            elif t1.isLeaf():
                j = len(t1.yield_())
                i -= j
                return False
            else:
                for kid in t1.children[::-1]:
                    if right_edge_helper(t, kid):
                        return True
                return False

        if right_edge_helper(self, self.getRoot()):
            return i
        else:
            raise RuntimeError("Tree is not a descendant of root.")

    def get_sister_index(self) -> int:
        if self.parent is None:
            return -1
        for i, child in enumerate(self.parent.children):
            if child is self:
                return i
        return -1

    def set_label(self, label: Optional[str]) -> None:
        if isinstance(label, str):
            self.label = self.normalize(label)
        else:
            raise TypeError(f"label must be str, not {type(label).__name__}")

    def set_parent(self, node: "Tree") -> None:
        self.parent = node

    def add_child(self, node: "Tree") -> None:
        node.set_parent(self)
        self.children.append(node)

    @classmethod
    def normalize(cls, text):
        return text.replace("-LRB-", "(").replace("-RRB-", ")")

    @classmethod
    def fromstring(cls, string: str, brackets: str = "()") -> Generator["Tree", None, None]:
        # TODO need more logging mesg to indicate whether "a b c d" or "(a b c d)" is parsed correctly
        # translated from CoreNLP's PennTreeReader
        # https://github.com/stanfordnlp/CoreNLP/blob/main/src/edu/stanford/nlp/trees/PennTreeReader.java#L144

        # this code block about `brackets` is borrowed from nltk
        # https://github.com/nltk/nltk/blob/develop/nltk/tree/tree.py#L641
        if not isinstance(brackets, str) or len(brackets) != 2:
            raise TypeError("brackets must be a length-2 string")
        if re.search(r"\s", brackets):
            raise TypeError("whitespace brackets not allowed")

        open_b, close_b = brackets
        open_pattern = re.escape(open_b)
        close_pattern = re.escape(close_b)

        # store `token_re` to avoid repeated regex compiling
        try:
            token_re = cls.token_re
        except AttributeError:
            token_re = re.compile(
                rf"(?x) [{open_pattern}{close_pattern}] | [^\s{open_pattern}{close_pattern}]+"
            )
            cls.token_re = token_re

        stack_parent: Deque["Tree"] = deque()
        current_tree = None

        tokens = peekable(token_re.findall(string))
        while (token := next(tokens, None)) is not None:
            if token == open_b:
                label = None if tokens.peek() == open_b else next(tokens, None)

                if label == close_b:
                    continue

                new_tree = cls(label)

                if current_tree is None:
                    stack_parent.append(new_tree)
                else:
                    current_tree.add_child(new_tree)
                    stack_parent.append(current_tree)

                current_tree = new_tree
            elif token == close_b:
                if len(stack_parent) == 0:
                    raise ValueError(
                        "failed to build tree from string with extra non-matching right"
                        " parentheses"
                    )
                else:
                    current_tree = stack_parent.pop()

                    if len(stack_parent) == 0:
                        yield cls._remove_extra_level(current_tree)

                        current_tree = None
                        continue
            else:
                if current_tree is None:
                    continue

                new_tree = cls(token)
                current_tree.add_child(new_tree)

        if current_tree is not None:  # type:ignore
            raise ValueError("incomplete tree (extra left parentheses in input)")

    @classmethod
    def _remove_extra_level(cls, root) -> "Tree":
        # get rid of extra levels of root with None label
        # e.g.: "((S (NP ...) (VP ...)))" -> "S (NP ...) (VP ...)"
        while root.label is None and len(root.children) == 1:
            root = root.children[0]
            root.parent = None
        return root

    def getRoot(self) -> "Tree":
        root_ = self
        while root_.parent is not None:
            root_ = root_.parent
        return root_

    def iter_upto_root(self) -> Generator["Tree", None, None]:
        """
        iterate up the tree from the current node to the root node.

        borrowed from anytree:
        https://github.com/c0fec0de/anytree/blob/27ff97eed4c09b4f0eb9ae61b45dd30b794a135c/anytree/node/nodemixin.py#L294
        """
        node = self
        while node.parent is not None:
            yield node
            node = node.parent

    @property
    def path(self):
        """
        return a path of nodes from root node down to `self`

        borrowed from anytree:
        https://github.com/c0fec0de/anytree/blob/27ff97eed4c09b4f0eb9ae61b45dd30b794a135c/anytree/node/nodemixin.py#L277
        """
        # use "reversed" because pyright complains about using "sorted"
        # convert to tuple to ensure unchangabel hereafter
        return tuple(reversed(list(self.iter_upto_root())))

    def walk_to(self, other: "Tree") -> Tuple[Tuple["Tree"], "Tree", Tuple["Tree"]]:
        """
        walk from `start` node to `end` node.

        returns (upwards, common, downwards):
            `upwards` is a list of nodes to go upward to.
            `common` the nearest sharing ancestor of `start` and `end`.
            `downwards` is a list of nodes to go downward to.

        modified from anytree:
        https://github.com/c0fec0de/anytree/blob/27ff97eed4c09b4f0eb9ae61b45dd30b794a135c/anytree/walker.py#L8
        """
        path_start = self.path
        path_end = other.path
        if self.getRoot() is not other.getRoot():
            raise ValueError("start and end are not part of the same tree.")

        # common
        common = tuple(
            node_start
            for node_start, node_end in zip(path_start, path_end)
            if node_start is node_end
        )
        assert common[0] is self.getRoot()
        len_common = len(common)

        # upwards
        if self is common[-1]:
            upwards: Tuple["Tree"] = tuple()  # type:ignore
        else:
            upwards: Tuple["Tree"] = tuple(reversed(path_start[len_common:]))  # type:ignore
        # down
        if other is common[-1]:
            down: Tuple["Tree"] = tuple()  # type:ignore
        else:
            down: Tuple["Tree"] = path_end[len_common:]  # type:ignore
        return upwards, common[-1], down

    @property
    def left_sisters(self) -> Optional[list]:
        sister_index_ = self.get_sister_index()
        is_not_the_first = sister_index_ is not None and sister_index_ > 0
        if is_not_the_first:
            return self.parent.children[:sister_index_]  # type:ignore
        return None

    @property
    def right_sisters(self) -> Optional[list]:
        sister_index_ = self.get_sister_index()
        is_not_the_last = sister_index_ is not None and sister_index_ < (
            len(self.parent.children) - 1  # type:ignore
        )
        if is_not_the_last:
            return self.parent.children[sister_index_ + 1 :]  # type:ignore
        return None

    def tostring(self) -> str:
        return repr(self)

    def preorder_iter(self) -> Generator["Tree", None, None]:
        if self:
            yield self
            for child in self.children:
                yield from child.preorder_iter()

    def getLeaves(self) -> List["Tree"]:
        """
        Gets the leaves of the tree.  All leaves nodes are returned as a list
        ordered by the natural left to right order of the tree.  None values,
        if any, are inserted into the list like any other value.

        return a list of the leaves.
        """
        leaves = []
        if self.isLeaf():
            leaves.append(self)
        else:
            for kid in self.children:
                leaves.extend(kid.getLeaves())
        return leaves

    def span_string(self) -> str:
        """
        Return String of leaves spanned by this tree
        """
        return " ".join(leaf.tostring() for leaf in self.getLeaves() if leaf is not None)

    def get_num_edges(self):
        """
        Return total number of edges across all nodes
        """
        if self.isLeaf():
            # print(f"{self.label=}\t1\t1")
            return 1, 1

        ns, weights = zip(*(kid.get_num_edges() for kid in self.children))
        descendant_n = sum(ns)
        descendant_weight = max(weights)

        if self.parent is None or self.parent.numChildren() == 1:
            # print(f"{self.label=}\t{descendant_n=}\t{descendant_weight=}")
            return descendant_n, descendant_weight

        ret_weight = descendant_weight + 1
        ret_n = descendant_n + ret_weight

        # print(f"{self.label=}\t{ret_n=}\t{ret_weight=}")
        return ret_n, ret_weight
