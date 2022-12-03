#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import re
import os
import sys
import subprocess
from typing import Tuple
from .structures import Structure


class Querier:
    method_tregex = "edu.stanford.nlp.trees.tregex.TregexPattern"

    def __init__(self, classpath: str):
        self.classpath = classpath

    def query(self, structure: Structure, fn_parsed: str) -> Tuple[int, str]:
        """
        Call Tregex to query {pattern} against {fn_parsed}

        :param pattern: Tregex pattern
        :param fn_parsed: parsed file by Stanford Parser
        :return (int) frequency: frequency of the pattern
        :return (str) matched_subtreees: matched subtrees of the pattern
        """
        print(f'\t[Tregex] Querying "{structure.desc}"...')
        cmd = (
            f'java -mx100m -cp "{self.classpath}"'
            f' {self.method_tregex} {structure.pat} "{fn_parsed}" -o'
        )
        try:
            p = subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as err_msg:
            print(err_msg)
            sys.exit(1)
        match_reslt = re.search(
            r"There were (\d+) matches in total\.", p.stderr.decode()
        )
        if match_reslt:
            freq = match_reslt.group(1)
        else:
            os.remove(fn_parsed)
            # Remove fn_parsed to make sure parsing will not be skipped on next running.
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
        matched_subtrees = p.stdout.decode()
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
