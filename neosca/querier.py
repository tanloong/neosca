#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from io import BytesIO
import logging
import os
import re
import sys
from tokenize import NAME, tokenize, untokenize
from typing import Optional

import jpype
from jpype import JClass

from .structure_counter import StructureCounter


class StanfordTregex:
    def __init__(
        self,
        classpaths: Optional[list] = None,
        max_memory: str = "3072m",
    ) -> None:
        self.classpaths = classpaths if classpaths is not None else []
        self.max_memory = max_memory
        self.TREGEX_PATTERN = "edu.stanford.nlp.trees.tregex.TregexPattern"
        self.STRING_READER = "java.io.StringReader"
        self.PENN_TREE_READER = "edu.stanford.nlp.trees.PennTreeReader"
        self.init_tregex()

    def init_tregex(self):
        if not jpype.isJVMStarted():  # pragma: no cover
            logging.info("starting JVM...")
            # Note that isJVMStarted may be renamed to isJVMRunning in the future.
            # In jpype's _core.py:
            # > TODO This method is horribly named.  It should be named isJVMRunning as
            # > isJVMStarted would seem to imply that the JVM was started at some
            # > point without regard to whether it has been shutdown.
            jpype.startJVM(f"-Xmx{self.max_memory}", classpath=self.classpaths)

        self.TregexPattern = jpype.JClass(self.TREGEX_PATTERN)
        self.StringReader = JClass(self.STRING_READER)
        self.PennTreeReader = JClass(self.PENN_TREE_READER)
        self.compiled_pattern_map = {}

    def query_pattern(self, s_name: str, pattern: str, trees: str) -> list:
        matched_subtrees = []
        if s_name not in self.compiled_pattern_map:
            tregex_pattern = self.TregexPattern.compile(pattern)
            self.compiled_pattern_map[s_name] = tregex_pattern
        else:
            tregex_pattern = self.compiled_pattern_map[s_name]

        treeReader = self.PennTreeReader(self.StringReader(trees))
        tree = treeReader.readTree()
        while tree is not None:
            matcher = tregex_pattern.matcher(tree)
            last_matching_root_node = None
            while matcher.find():
                match = matcher.getMatch()
                # Each tree node can be reported only once as the root of a match.
                # Although solely nodeNumber checking is enough, it involves
                # iteration acorss the tree, which can be slow on high trees,
                # so use equals() to exit if-condition sooner. The equals()
                # will check labels, number of children, and finally whether
                # the children are pairwise equal. This achieves an average
                # speed increase of 78ms across 4 trials on ~5% fragment of
                # Penn Treebank.
                if last_matching_root_node is not None and (
                    last_matching_root_node.equals(match)
                    and last_matching_root_node.nodeNumber(tree) == match.nodeNumber(tree)
                ):
                    continue
                last_matching_root_node = match

                # we don't use match.spanString() because the output lacks
                # whitespace, e.g., "the media" becomes "themedia"
                span_string = " ".join(str(leaf.toString()) for leaf in match.getLeaves())
                penn_string = str(match.pennString().replaceAll("\r", ""))
                matched_subtrees.append(span_string + "\n" + penn_string)
            tree = treeReader.readTree()
        return matched_subtrees

    def set_value(self, counter: StructureCounter, s_name: str, trees: str) -> None:
        value = counter.get_value(s_name)
        if value is not None:
            return

        structure = counter.get_structure(s_name)
        tregex_pattern = structure.tregex_pattern
        if tregex_pattern is not None:
            logging.info(f"Searching for {s_name} ({structure.desc})...")
            matched_subtrees = self.query_pattern(s_name, tregex_pattern, trees)
            counter.set_matches(s_name, matched_subtrees)
            counter.set_value(s_name, len(matched_subtrees))
            return

        # else evaluate value_source
        value_source = structure.value_source
        assert value_source is not None, f"value_source for {s_name} is None."

        tokens = []
        g = tokenize(BytesIO(value_source.encode("utf-8")).readline)
        next(g)  # skip the "utf-8" token
        for toknum, tokval, *_ in g:
            if toknum == NAME:
                self.set_value(counter, tokval, trees)
                tokens.append((toknum, f"counter.get_structure('{tokval}')"))
            elif tokval in ("+", "-", "*", "/", "(", ")"):
                tokens.append((toknum, tokval))
            elif tokval != "":
                raise ValueError(f"Unexpected token: '{tokval}'")
        logging.info(f"Calculating {s_name} = {value_source}...")
        counter.set_value(s_name, eval(untokenize(tokens)))

    def query(
        self,
        counter: StructureCounter,
        trees: str,
        is_reserve_matched: bool = False,
        odir_matched: str = "",
        is_stdout: bool = False,
    ):
        for s_name in counter.selected_measures:
            if s_name == "W":
                logging.info('Searching for "words"')
                value = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
                counter.set_value(s_name, value)
                continue

            self.set_value(counter, s_name, trees)

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
        for s_name in counter.selected_measures:
            matches = counter.get_matches(s_name)
            if matches is None or len(matches) == 0:
                return

            res = "\n".join(matches)
            # only accept alphanumeric chars, underscore, and hypen
            escaped_s_name = re.sub(r"[^\w-]", "", s_name.replace("/", "-per-"))
            matches_id = bn_input_noext + "-" + escaped_s_name
            if not is_stdout:
                extension = ".matched"
                fn_match_output = os.path.join(subodir_matched, matches_id + extension)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(res)
            else:
                sys.stdout.write(matches_id + "\n")
                sys.stdout.write(res)
