#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import re
import subprocess
import sys
from typing import Tuple

from .structures import Structure
from .structures import Structures


class StanfordTregex:
    TREGEX_METHOD = "edu.stanford.nlp.trees.tregex.TregexPattern"
    MAX_MEMORY = "100m"

    def __init__(
        self,
        dir_stanford_tregex: str = "",
        max_memory: str = MAX_MEMORY,
    ) -> None:
        self.classpath = dir_stanford_tregex + os.sep + "stanford-tregex.jar"
        self.max_memory = max_memory

    def query_structure(self, pattern: str, trees: str, reserve_matched:bool=False) -> Tuple[int, str]:
        """Call Tregex to query {pattern} against {ofile_parsed}"""
        cmd = [
            "java",
            f"-mx{self.max_memory}",
            "-cp",
            self.classpath,
            self.TREGEX_METHOD,
            pattern,
            "-o",
            "-filter",
        ]
        try:
            p = subprocess.run(
                cmd,
                input=trees.encode("utf-8"),
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as err_msg:
            print(err_msg)
            sys.exit(1)
        match_reslt = re.search(r"There were (\d+) matches in total\.", p.stderr.decode("utf-8"))
        if match_reslt:
            freq = match_reslt.group(1)
        else:
            sys.exit(
                "Error: failed to obtain frequency. It is likely that:\n"
                "(1) Tregex's interface has"
                " changed. As a workaround, download an older version, v4.2.0,"
                " for example. If Tregex's interface does have changed, the"
                " latest version of Tregex will be supported in next few"
                " releases.\n"
                "(2) You manually modified Tregex patterns in"
                " structures.py. Make sure that: on Windows, those patterns are"
                " enclosed by double quotes; on Linux and macOS they are"
                " surrounded by single quotes."
            )
        matched_subtrees = p.stdout.decode("utf-8")
        if reserve_matched:
            matched_subtrees = self._add_terms(matched_subtrees)
        return int(freq), matched_subtrees

    def query(self, structures: Structures, trees: str, reserve_matched:bool=False, odir_matched:str=''):
        for structure in structures.to_query:
            print(f'\t[Tregex] Querying "{structure.desc}"...')
            structure.freq, structure.matches = self.query_structure(structure.pat, trees, reserve_matched)
        if reserve_matched:
            self.write_match_output(structures, odir_matched)
        return structures

    def _add_terms(self, subtrees: str) -> str:
        """
        Add terminals above each subtree

        :param subtrees: matched subtrees by Tregex
         e.g. (NP (NNP Mr.) (NNP Reed))
        :return: e.g.
         Mr. Reed
         (NP (NNP Mr.) (NNP Reed))
        """
        result = ""
        pattern = r"([^\s)]+)\)"
        for subtree in re.split(r"(?:\r?\n){2,}", subtrees):
            terminals = " ".join(re.findall(pattern, subtree))
            result += f"{terminals}\n{subtree}\n\n"
        return result.strip()

    def write_match_output(self, structures: Structures, odir_matched:str='') -> None:
        """
        Save Tregex's match output

        :param structures: an instance of Structures
        """
        bn_input = os.path.basename(structures.ifile)
        bn_input_noext = os.path.splitext(bn_input)[0]
        subdir_match_output = os.path.join(odir_matched, bn_input_noext).strip()
        if not os.path.isdir(subdir_match_output):
            # if not (exists and is a directory)
            os.makedirs(subdir_match_output)
        for structure in structures.to_query:
            if structure.matches:
                bn_match_output = bn_input_noext + "-" + structure.name.replace("/", "p") + ".matches"
                fn_match_output = os.path.join(subdir_match_output, bn_match_output)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(structure.matches)
