#!/usr/bin/env python3

import re
from typing import Generator, Iterable, Iterator, List, NamedTuple, Optional

from neosca_gui.ng_tregex.tree import Tree


class Named_Nodes:
    def __init__(self, name: Optional[str], nodes: Optional[List[Tree]], string_repr: str = "") -> None:
        self.name = name
        self.nodes = nodes
        self.string_repr = string_repr

    def set_name(self, new_name: Optional[str]) -> None:
        self.name = new_name

    def set_nodes(self, new_nodes: List[Tree]) -> None:
        self.nodes = new_nodes


class Node_Description(NamedTuple):
    op: "Node_Op"
    value: str


class Node_Descriptions:
    def __init__(
        self,
        node_descriptions: List[Node_Description],
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> None:
        self.descriptions = node_descriptions
        self.is_negated = is_negated
        self.use_basic_cat = use_basic_cat

        self.name = None
        self.string_repr = "".join(desc.value for desc in self.descriptions)

    def __iter__(self) -> Iterator[Node_Description]:
        return iter(self.descriptions)

    def __repr__(self) -> str:
        return self.string_repr

    def has_name(self) -> bool:
        return self.name is not None

    def set_name(self, name: str) -> None:
        self.name = name

    def set_string_repr(self, s: str):
        self.string_repr = s

    def add_description(self, other_description: Node_Description) -> None:
        self.descriptions.append(other_description)

    def toggle_negated(self) -> None:
        self.is_negated = not self.is_negated

    def toggle_use_basic_cat(self) -> None:
        self.use_basic_cat = not self.use_basic_cat

    def satisfy(self, t: Tree) -> bool:
        for desc in self.descriptions:
            if desc.op.satisfies(t, desc.value, is_negated=self.is_negated, use_basic_cat=self.use_basic_cat):
                return True
        return False

    def searchNodeIterator(self, t: Tree) -> Generator[Tree, None, None]:
        for node in t.preorder_iter():
            if self.satisfy(node):
                yield node


class Node_Op:
    @classmethod
    def satisfies(
        cls,
        node: Tree,
        expect: str,
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> bool:
        raise NotImplementedError()

    @classmethod
    def in_(
        cls,
        node: Tree,
        expects: Iterable[str],
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> bool:
        return any(
            cls.satisfies(node, expect, is_negated=is_negated, use_basic_cat=use_basic_cat)
            for expect in expects
        )


class Node_Text(Node_Op):
    @classmethod
    def satisfies(
        cls, node: Tree, expect: str, *, is_negated: bool = False, use_basic_cat: bool = False
    ) -> bool:
        attr = "basic_category" if use_basic_cat else "label"
        value = getattr(node, attr)

        if value is None:
            return is_negated
        else:
            return (value == expect) != is_negated


class Node_Regex(Node_Op):
    @classmethod
    def satisfies(
        cls, node: Tree, expect: str, *, is_negated: bool = False, use_basic_cat: bool = False
    ) -> bool:
        attr = "basic_category" if use_basic_cat else "label"
        value = getattr(node, attr)

        if value is None:
            return is_negated
        else:
            # Convert regex to standard python regex
            flag = ""
            current_flag = value[-1]
            while current_flag != "/":
                # Seems that only (?m) and (?x) are useful for node describing:
                #  re.ASCII      (?a)
                #  re.IGNORECASE (?i)
                #  re.LOCALE     (?L)
                #  re.DOTALL     (?s)
                #  re.MULTILINE  (?m)
                #  re.VERBOSE    (?x)
                if current_flag not in "xi":
                    raise ValueError(f"Error!! Unsupported regexp flag: {current_flag}")
                flag += current_flag
                value = value[:-1]
                current_flag = value[-1]

            value = value[1:-1]
            if flag:
                value = "(?" + "".join(set(flag)) + ")" + value

            return (re.search(value, expect) is not None) != is_negated


class Node_Any(Node_Op):
    @classmethod
    def satisfies(
        cls,
        node: Tree,
        expect: str = "",
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> bool:
        return not is_negated


class Node_Root(Node_Op):
    @classmethod
    def satisfies(
        cls,
        node: Tree,
        expect: str = "",
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> bool:
        return (node.parent is None) != is_negated
