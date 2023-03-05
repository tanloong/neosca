#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import re
from typing import Tuple

import jpype
from jpype import JClass

from .structure_counter import StructureCounter


class StanfordTregex:
    TREGEX_METHOD = "edu.stanford.nlp.trees.tregex.TregexPattern"
    MAX_MEMORY = "3072m"

    def __init__(
        self,
        dir_stanford_tregex: str = "",
        max_memory: str = MAX_MEMORY,
    ) -> None:
        self.classpath = os.path.join(dir_stanford_tregex, "stanford-tregex.jar")
        self.max_memory = max_memory
        self.init_tregex()

    def init_tregex(self):
        if not jpype.isJVMStarted():
            # Note that isJVMStarted may be renamed to isJVMRunning in the future.
            # In jpype's _core.py:
            # > TODO This method is horribly named.  It should be named isJVMRunning as
            # > isJVMStarted would seem to imply that the JVM was started at some
            # > point without regard to whether it has been shutdown.
            jpype.startJVM(f"-Xmx{self.max_memory}", classpath=self.classpath)
        else:
            jpype.addClassPath(self.classpath)

        self.TregexPattern = jpype.JClass("edu.stanford.nlp.trees.tregex.TregexPattern")
        self.StringReader = JClass("java.io.StringReader")
        self.PennTreeReader = JClass("edu.stanford.nlp.trees.PennTreeReader")
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
    ):
        for structure in counter.structures_to_query:
            print(f'\t[Tregex] Querying "{structure.desc}"...')
            if structure.name == "W":
                structure.freq = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
                continue
            structure.freq, structure.matches = self.query_pattern(
                structure.name, structure.pattern, trees
            )
        if is_reserve_matched:
            self.write_match_output(counter, odir_matched)
        return counter

    def write_match_output(self, counter: StructureCounter, odir_matched: str = "") -> None:
        """
        Save Tregex's match output

        :param structures: an instance of Structures
        """
        bn_input = os.path.basename(counter.ifile)
        bn_input_noext = os.path.splitext(bn_input)[0]
        subdir_match_output = os.path.join(odir_matched, bn_input_noext).strip()
        if not os.path.isdir(subdir_match_output):
            # if not (exists and is a directory)
            os.makedirs(subdir_match_output)
        for structure in counter.structures_to_query:
            if structure.matches:
                bn_match_output = (
                    bn_input_noext + "-" + structure.name.replace("/", "p") + ".matches"
                )
                fn_match_output = os.path.join(subdir_match_output, bn_match_output)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    for match in structure.matches:
                        f.write(match + "\n")
