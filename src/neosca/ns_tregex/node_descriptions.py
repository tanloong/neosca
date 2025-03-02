#!/usr/bin/env python3

import re
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable, Iterator
from typing import NamedTuple

from typing_extensions import override

from ..ns_tregex.tree import Tree


class NamedNodes:
    def __init__(self, name: str | None, nodes: list[Tree] | None, strins_repr: str = "") -> None:
        self.name = name
        self.nodes = nodes
        self.strins_repr = strins_repr

    def set_name(self, new_name: str | None) -> None:
        self.name = new_name

    def set_nodes(self, new_nodes: list[Tree]) -> None:
        self.nodes = new_nodes


class NodeDescription(NamedTuple):
    op: "NodeOp"
    value: str


class NodeDescriptions:
    def __init__(
        self,
        node_descriptions: list[NodeDescription],
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> None:
        self.descriptions = node_descriptions
        self.is_negated = is_negated
        self.use_basic_cat = use_basic_cat

        self.name: str | None = None
        self.strins_repr = "".join(desc.value for desc in self.descriptions)

    def __iter__(self) -> Iterator[NodeDescription]:
        return iter(self.descriptions)

    def __repr__(self) -> str:
        return self.strins_repr

    def has_name(self) -> bool:
        return self.name is not None

    def set_name(self, name: str) -> None:
        self.name = name

    def set_strins_repr(self, s: str):
        self.strins_repr = s

    def add_description(self, other_description: NodeDescription) -> None:
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

    def search_node_iterator(self, t: Tree) -> Generator[Tree, None, None]:
        for node in t.visit():
            if self.satisfy(node):
                yield node


class NodeOp(ABC):
    @classmethod
    @abstractmethod
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


class NodeText(NodeOp):
    @classmethod
    @override
    def satisfies(
        cls, node: Tree, expect: str, *, is_negated: bool = False, use_basic_cat: bool = False
    ) -> bool:
        attr = "basic_category" if use_basic_cat else "label"
        value = getattr(node, attr)

        if value is None:
            return is_negated
        else:
            return (value == expect) != is_negated


class NodeRegex(NodeOp):
    @classmethod
    @override
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


class NodeAny(NodeOp):
    @classmethod
    @override
    def satisfies(
        cls,
        node: Tree,
        expect: str = "",
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> bool:
        return not is_negated


class NodeRoot(NodeOp):
    @classmethod
    @override
    def satisfies(
        cls,
        node: Tree,
        expect: str = "",
        *,
        is_negated: bool = False,
        use_basic_cat: bool = False,
    ) -> bool:
        return (node.parent is None) != is_negated
