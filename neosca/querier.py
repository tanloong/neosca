#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import logging
import os
import re
import sys
from typing import Tuple

import jpype
from jpype import JClass

from .structure_counter import StructureCounter


class StanfordTregex:
    def __init__(
        self,
        stanford_tregex_home: str = "",
        max_memory: str = "3072m",
    ) -> None:
        self.classpath = os.path.join(stanford_tregex_home, "stanford-tregex.jar")
        self.max_memory = max_memory
        self.TREGEX_PATTERN = "edu.stanford.nlp.trees.tregex.TregexPattern"
        self.STRING_READER = "java.io.StringReader"
        self.PENN_TREE_READER = "edu.stanford.nlp.trees.PennTreeReader"
        self.init_tregex()

    def init_tregex(self):
        if not jpype.isJVMStarted():  # pragma: no cover
            # Note that isJVMStarted may be renamed to isJVMRunning in the future.
            # In jpype's _core.py:
            # > TODO This method is horribly named.  It should be named isJVMRunning as
            # > isJVMStarted would seem to imply that the JVM was started at some
            # > point without regard to whether it has been shutdown.
            jpype.startJVM(f"-Xmx{self.max_memory}", classpath=self.classpath)
        else:
            jpype.addClassPath(self.classpath)

        self.TregexPattern = jpype.JClass(self.TREGEX_PATTERN)
        self.StringReader = JClass(self.STRING_READER)
        self.PennTreeReader = JClass(self.PENN_TREE_READER)
        self.patname_patobj = {}

    def query_pattern(self, patname: str, pattern: str, trees: str) -> Tuple[int, list]:
        matched_subtrees = []
        if patname not in self.patname_patobj:
            tregex_pattern = self.TregexPattern.compile(pattern)
            self.patname_patobj[patname] = tregex_pattern
        else:
            tregex_pattern = self.patname_patobj[patname]

        treeReader = self.PennTreeReader(self.StringReader(trees))
        tree = treeReader.readTree()
        while tree is not None:
            matcher = tregex_pattern.matcher(tree)
            last_matching_root_node = None
            while matcher.find():
                match = matcher.getMatch()
                if last_matching_root_node is not None and last_matching_root_node == match:
                    # implement Tregex's -o option: https://github.com/stanfordnlp/CoreNLP/blob/efc66a9cf49fecba219dfaa4025315ad966285cc/src/edu/stanford/nlp/trees/tregex/TregexPattern.java#L885
                    continue
                last_matching_root_node = match
                span_string = " ".join(str(leaf.toString()) for leaf in match.getLeaves())
                # we don't use match.spanString() because the output lacks whitespace, e.g., "the media" becomes "themedia"
                penn_string = str(match.pennString().replaceAll("\r", ""))
                matched_subtrees.append(span_string + "\n" + penn_string)
            tree = treeReader.readTree()
        return len(matched_subtrees), matched_subtrees

    def query(
        self,
        counter: StructureCounter,
        trees: str,
        is_reserve_matched: bool = False,
        odir_matched: str = "",
        is_stdout: bool = False,
    ):
        for structure in counter.structures_to_query:
            logging.info(f'[Tregex] Querying "{structure.desc}"...')
            if structure.name == "W":
                structure.freq = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
                continue
            structure.freq, structure.matches = self.query_pattern(
                structure.name, structure.pattern, trees
            )
        if is_reserve_matched:  # pragma: no cover
            self.write_match_output(counter, odir_matched, is_stdout)
        return counter

    def write_match_output(
        self, counter: StructureCounter, odir_matched: str = "", is_stdout: bool = False
    ) -> None:  # pragma: no cover
        """
        Save Tregex's match output
        """
        bn_input = os.path.basename(counter.ifile)
        bn_input_noext = os.path.splitext(bn_input)[0]
        subodir_matched = os.path.join(odir_matched, bn_input_noext).strip()
        if not is_stdout:
            os.makedirs(subodir_matched, exist_ok=True)
        for structure in counter.structures_to_query:
            if structure.matches:
                matches = "\n".join(structure.matches)
                matches_id = bn_input_noext + "-" + structure.name.replace("/", "p")
                if not is_stdout:
                    extension = ".matched"
                    fn_match_output = os.path.join(subodir_matched, matches_id + extension)
                    with open(fn_match_output, "w", encoding="utf-8") as f:
                        f.write(matches)
                else:
                    sys.stdout.write(matches_id + "\n")
                    sys.stdout.write(matches)
