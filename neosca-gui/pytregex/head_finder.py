#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tree import Tree


class HeadFinder:
    def determineHead(self, t: "Tree"):
        raise NotImplementedError
