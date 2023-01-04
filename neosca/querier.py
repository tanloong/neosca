#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import re
import os
import sys
import subprocess
from typing import Tuple
from .structures import Structure


class Querier:
    TREGEX_METHOD = "edu.stanford.nlp.trees.tregex.TregexPattern"
    MAX_MEMORY = "100m"

    def __init__(self, dir_stanford_tregex: str, max_memory=MAX_MEMORY) -> None:
        self.classpath = '"' + dir_stanford_tregex + os.sep + "stanford-tregex.jar" + '"'
        self.max_memory = max_memory

    def query(self, structure: Structure, trees: str) -> Tuple[int, str]:
        """Call Tregex to query {pattern} against {ofile_parsed}"""
        print(f'\t[Tregex] Querying "{structure.desc}"...')
        cmd = (
            f'java -mx{self.max_memory} -cp "{self.classpath}"'
            f" {self.TREGEX_METHOD} {structure.pat} -o -filter"
        )
        try:
            p = subprocess.run(
                cmd,
                input=trees.encode("utf-8"),
                shell=True,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as err_msg:
            print(err_msg)
            sys.exit(1)
        match_reslt = re.search(
            r"There were (\d+) matches in total\.", p.stderr.decode("utf-8")
        )
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
        matched_subtrees = self._add_terms(matched_subtrees)
        return int(freq), matched_subtrees

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
