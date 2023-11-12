from typing import TYPE_CHECKING, List, Optional, Set

from .head_finder import HeadFinder

# translated from https://github.com/stanfordnlp/CoreNLP/blob/main/src/edu/stanford/nlp/trees/AbstractCollinsHeadFinder.java
# last modified at Oct 1, 2021 (https://github.com/stanfordnlp/CoreNLP/commits/main/src/edu/stanford/nlp/trees/AbstractCollinsHeadFinder.java)

if TYPE_CHECKING:
    from .tree import Tree


class AbstractCollinsHeadFinder(HeadFinder):
    def __init__(self, *categoriesToAvoid) -> None:
        self.nonTerminalInfo: Optional[dict] = None
        self.pennPunctTags: Set[str] = {"''``", "-LRB-", "-RRB-", ".", ":", ","}
        self.defaultRule: Optional[list] = None

        # automatically build defaultLeftRule, defaultRightRule
        if categoriesToAvoid:
            self.defaultLeftRule = ["leftexcept"] + list(categoriesToAvoid)
            self.defaultRightRule = ["rightexcept"] + list(categoriesToAvoid)
        else:
            self.defaultLeftRule = ["left"]
            self.defaultRightRule = ["right"]

        self._how_map = {
            "left": self.findLeftHead,
            "leftdis": self.findLeftDisHead,
            "leftexcept": self.findLeftExceptHead,
            "right": self.findRightHead,
            "rightdis": self.findRightDisHead,
            "rightexcept": self.findRightExceptHead,
        }

    def findMarkedHead(self, t: "Tree"):
        return None

    def determineHead(self, t: "Tree") -> Optional["Tree"]:
        """
        Determine which daughter of the current parse tree is the head.

        param t The parse tree to examine the daughters of.
        return The daughter parse tree that is the head of t.
        Returns None for leaf nodes.
        """
        if self.nonTerminalInfo is None:
            raise ValueError(
                "Classes derived from AbstractCollinsHeadFinder must create and fill HashMap" " nonTerminalInfo."
            )

        if not t or t.isLeaf():
            # raise ValueError("Can't return head of empty or leaf "Tree".")
            return None

        kids = t.children

        theHead = self.findMarkedHead(t)
        if theHead is not None:
            return theHead

        # if the node is a unary, then that kid must be the head
        # it used to special case preterminal and ROOT/TOP case
        # but that seemed bad (especially hardcoding string "ROOT")
        if len(kids) == 1:
            return kids[0]

        return self.determineNonTrivialHead(t)

    def determineNonTrivialHead(self, t) -> Optional["Tree"]:
        """
        Called by determineHead and may be overridden in subclasses if special
        treatment is necessary for particular categories.

        param t The tre to determine the head daughter of param parent The parent of t (or may be None)
        return The head daughter of t
        """
        theHead: Optional["Tree"] = None
        motherCat = t.label
        if motherCat.startswith("@"):
            motherCat = motherCat[1:]
        if self.nonTerminalInfo is not None and motherCat not in self.nonTerminalInfo:
            return None

        hows: List[List[str]] = self.nonTerminalInfo.get(motherCat, None)  # type:ignore
        kids = t.children
        if hows is None:
            if self.defaultRule is not None:
                return self.traverseLocate(kids, self.defaultRule, True)
            else:
                raise ValueError(f"No head rule defined for {motherCat}")

        for i in range(len(hows)):
            lastResort = i == (len(hows) - 1)
            theHead = self.traverseLocate(kids, hows[i], lastResort)
            if theHead is not None:
                break
        return theHead

    def traverseLocate(self, daughterTrees: List["Tree"], how: List[str], lastResort: bool) -> Optional["Tree"]:
        """
        Attempt to locate head daughter tree from among daughters. Go through
        daughterTrees looking for things from or not in a set given by the
        contents of the list how, and if you do not find one, take leftmost or
        rightmost perhaps matching thing if lastResort is true, otherwise
        return None.
        """
        try:
            headIdx = self._how_map[how[0]](daughterTrees, how)
        except KeyError:
            raise ValueError("Invalid direction type")
        if headIdx < 0:
            if lastResort:
                # use the default rule to try to match anything except
                # categoriesToAvoid if that doesn't match, we'll return the
                # left or rightmost child (by setting headIdx).  We want to be
                # careful to ensure that postOperationFix runs exactly once.
                if how[0].startswith("left"):
                    headIdx = 0
                    rule = self.defaultLeftRule
                else:
                    headIdx = len(daughterTrees) - 1
                    rule = self.defaultRightRule

                child = self.traverseLocate(daughterTrees, rule, False)
                if child is not None:
                    return child
                else:
                    return daughterTrees[headIdx]
            else:
                return None

        headIdx = self.postOperationFix(headIdx, daughterTrees)
        return daughterTrees[headIdx]

    def findLeftHead(self, daughterTrees: List["Tree"], how: List[str]):  # {{{
        for i in range(1, len(how)):
            for headIdx in range(len(daughterTrees)):
                childCat = daughterTrees[headIdx].label
                if how[i] == childCat:
                    return headIdx
        return -1

    def findLeftDisHead(self, daughterTrees: List["Tree"], how: List[str]):
        for headIdx in range(len(daughterTrees)):
            childCat = daughterTrees[headIdx].label
            for i in range(1, len(how)):
                if how[i] == childCat:
                    return headIdx
        return -1

    def findLeftExceptHead(self, daughterTrees: List["Tree"], how: List[str]):
        for headIdx in range(len(daughterTrees)):
            childCat = daughterTrees[headIdx].label
            found = True
            for i in range(1, len(how)):
                if how[i] == childCat:
                    found = False
            if found:
                return headIdx
        return -1

    def findRightHead(self, daughterTrees: List["Tree"], how: List[str]):
        for i in range(1, len(how)):
            for headIdx in range(len(daughterTrees) - 1, -1, -1):
                childCat = daughterTrees[headIdx].label
                if how[i] == childCat:
                    return headIdx
        return -1

    # from right, but search for any of the categories, not by category in turn
    def findRightDisHead(self, daughterTrees: List["Tree"], how: List[str]):
        for headIdx in range(len(daughterTrees) - 1, -1, -1):
            childCat = daughterTrees[headIdx].label
            for i in range(1, len(how)):
                if how[i] == childCat:
                    return headIdx
        return -1

    def findRightExceptHead(self, daughterTrees: List["Tree"], how: List[str]):
        for headIdx in range(len(daughterTrees) - 1, -1, -1):
            childCat = daughterTrees[headIdx].label
            found = True
            for i in range(1, len(how)):
                if how[i] == childCat:
                    found = False
            if found:
                return headIdx
        return -1

    # }}}
    def postOperationFix(self, headIdx: int, daughterTrees: List["Tree"]) -> int:
        return headIdx
