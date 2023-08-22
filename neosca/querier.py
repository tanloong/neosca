#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from io import BytesIO
import logging
import os
import os.path as os_path
import re
import sys
from tokenize import NAME, NUMBER, PLUS, tokenize, untokenize
from typing import List, Optional, TYPE_CHECKING

import jpype
from jpype import JClass

from .scaexceptions import CircularDefinitionError, InvalidSourceError

if TYPE_CHECKING:
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
            logging.debug("[StanfordTregex] starting JVM...")
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

    def get_compiled_pattern(self, sname: str, pattern_string: str):
        if sname not in self.compiled_pattern_map:
            tregex_pattern = self.TregexPattern.compile(pattern_string)
            self.compiled_pattern_map[sname] = tregex_pattern
        else:
            tregex_pattern = self.compiled_pattern_map[sname]

        return tregex_pattern

    def get_matches(self, sname: str, pattern_string: str, trees: str) -> list:
        matches = []
        tregex_pattern = self.get_compiled_pattern(sname, pattern_string)

        treeReader = self.PennTreeReader(self.StringReader(trees))
        tree = treeReader.readTree()
        while tree is not None:
            matcher = tregex_pattern.matcher(tree)
            last_matching_root_node = None
            while matcher.find():
                match = matcher.getMatch()
                # Each tree node can be reported only once as the root of a match.
                # Although solely nodeNumber checking is enough, it involves
                #  iteration acorss the tree, which can be slow on high trees,
                #  so use equals() to exit if-condition early. The equals()
                #  will check labels, number of children, and finally whether
                #  the children are pairwise equal. This achieves an average
                #  speed increase of 78ms across 4 trials on ~5% fragment of
                #  Penn Treebank
                #  (https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/treebank.zip).
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
                matches.append(span_string + "\n" + penn_string)
            tree = treeReader.readTree()
        return matches

    @classmethod
    def check_circular_def(
        cls, descendant_sname: str, ancestor_snames: List[str], counter: "StructureCounter"
    ) -> None:
        if descendant_sname in ancestor_snames:
            circular_definition = ", ".join(
                f"{upstream_sname} = {counter.get_structure(upstream_sname).value_source}"
                for upstream_sname in ancestor_snames
            )
            raise CircularDefinitionError(f"Circular definition: {circular_definition}")
        else:
            logging.debug(
                "[StanfordTregex] Circular definition check passed: descendant"
                f" {descendant_sname} not in ancestors {ancestor_snames}"
            )

    def tokenize_value_source(
        self,
        value_source: str,
        counter: "StructureCounter",
        sname: str,
        trees: str,
        ancestor_snames: List[str],
    ) -> list:
        tokens = []
        g = tokenize(BytesIO(value_source.encode("utf-8")).readline)
        next(g)  # skip the "utf-8" token
        for toknum, tokval, *_ in g:
            if toknum == NAME:
                ancestor_snames.append(sname)
                StanfordTregex.check_circular_def(tokval, ancestor_snames, counter)

                self.set_value(counter, tokval, trees, ancestor_snames)
                if self.has_tregex_pattern(counter, tokval):
                    ancestor_snames.clear()

                tokens.append((toknum, f"counter.get_structure('{tokval}')"))
            elif toknum == NUMBER:
                tokens.append((toknum, tokval))
            elif tokval in ("+", "-", "*", "/", "(", ")"):
                tokens.append((toknum, tokval))
            # constrain value_source as only NAMEs and numberic ops to assure security for `eval`
            elif tokval != "":
                raise InvalidSourceError(f'Unexpected token: "{tokval}"')
        # append "+ 0" to force tokens evaluated as num if value_source contains just name of another Structure
        tokens.extend(((PLUS, "+"), (NUMBER, "0")))
        return tokens

    def has_tregex_pattern(self, counter: "StructureCounter", sname: str) -> bool:
        return counter.get_structure(sname).tregex_pattern is not None

    def set_value_from_pattern(self, counter: "StructureCounter", sname: str, trees: str):
        structure = counter.get_structure(sname)
        tregex_pattern = structure.tregex_pattern
        assert tregex_pattern is not None

        logging.info(
            f" Searching for {sname}"
            + (f" ({structure.description})..." if structure.description is not None else "...")
        )
        logging.debug(f" Searching for {tregex_pattern}")
        matched_subtrees = self.get_matches(sname, tregex_pattern, trees)
        counter.set_matches(sname, matched_subtrees)
        counter.set_value(sname, len(matched_subtrees))

    def set_value_from_source(
        self, counter: "StructureCounter", sname: str, trees: str, ancestor_snames: List[str]
    ) -> None:
        structure = counter.get_structure(sname)
        value_source = structure.value_source
        assert value_source is not None, f"value_source for {sname} is None."

        logging.info(
            f" Calculating {sname} "
            + (f"({structure.description}) " if structure.description is not None else "")
            + f"= {value_source}..."
        )
        tokens = self.tokenize_value_source(value_source, counter, sname, trees, ancestor_snames)
        value = eval(untokenize(tokens))
        counter.set_value(sname, value)

    def set_value(
        self,
        counter: "StructureCounter",
        sname: str,
        trees: str,
        ancestor_snames: List[str] = [],
    ) -> None:
        value = counter.get_value(sname)
        if value is not None:
            logging.debug(
                f"[StanfordTregex] {sname} has already been set as {value}, skipping..."
            )
            return

        if sname == "W":
            logging.info(' Searching for "words"')
            value = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
            counter.set_value(sname, value)
            return

        if self.has_tregex_pattern(counter, sname):
            self.set_value_from_pattern(counter, sname, trees)
        else:
            self.set_value_from_source(counter, sname, trees, ancestor_snames)

    def set_all_values(self, counter: "StructureCounter", trees: str) -> None:
        for sname in counter.selected_measures:
            self.set_value(counter, sname, trees)

    def query(
        self,
        counter: "StructureCounter",
        trees: str,
        is_reserve_matched: bool = False,
        odir_matched: str = "",
        is_stdout: bool = False,
    ) -> "StructureCounter":
        self.set_all_values(counter, trees)

        if is_reserve_matched:  # pragma: no cover
            self.write_match_output(counter, odir_matched, is_stdout)
        return counter

    def write_match_output(
        self, counter: "StructureCounter", odir_matched: str = "", is_stdout: bool = False
    ) -> None:  # pragma: no cover
        """
        Save Tregex's match output
        """
        bn_input = os_path.basename(counter.ifile)
        bn_input_noext = os_path.splitext(bn_input)[0]
        subodir_matched = os_path.join(odir_matched, bn_input_noext).strip()
        if not is_stdout:
            os.makedirs(subodir_matched, exist_ok=True)
        for sname, structure in counter.sname_structure_map.items():
            matches = structure.matches
            if matches is None or len(matches) == 0:
                continue

            meta_data = (
                f"# name: {structure.name}\n"
                + f"# description: {structure.description}\n"
                + f"# tregex_pattern: {structure.tregex_pattern}\n\n"
            )
            res = "\n".join(matches)
            # only accept alphanumeric chars, underscore, and hypen
            escaped_sname = re.sub(r"[^\w-]", "", sname.replace("/", "-per-"))
            matches_id = bn_input_noext + "-" + escaped_sname
            if not is_stdout:
                extension = ".matched"
                fn_match_output = os_path.join(subodir_matched, matches_id + extension)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(meta_data)
                    f.write(res)
            else:
                sys.stdout.write(matches_id + "\n")
                sys.stdout.write(meta_data)
                sys.stdout.write(res)
