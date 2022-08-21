import os
from os import path
import re
import subprocess
import sys

from .structures import Structures


class Analyzer:
    def __init__(self, dir_parser, dir_tregex):
        """
        :param dir_parser: directory to Stanford Parser
        :param dir_tregex: directory to Tregex
        """
        self.classpath_parser = '"' + dir_parser + os.sep + "*" + '"'
        self.classpath_tregex = (
            '"' + dir_tregex + os.sep + "stanford-tregex.jar" + '"'
        )

    def _parse(self, fn_input: str, fn_parsed: str):
        """
        Call Stanford Parser

        :param fn_input: file to parse
        :param fn_parsed: where to save the parsed results
        :return: None
        """
        method = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
        model = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
        cmd = (
            f"java -mx1500m -cp {self.classpath_parser} {method} "
            f"-outputFormat penn {model} {fn_input} > {fn_parsed}"
        )
        if not path.exists(fn_parsed):  # if FILE does not exist
            # print(f"{fn_parsed} does not exist, running Stanford Parser...")
            subprocess.run(cmd, shell=True, capture_output=True)
            return
        mt_input = path.getmtime(fn_input)  # get the last modification time
        mt_parsed = path.getmtime(fn_parsed)
        if mt_input > mt_parsed:
            # print(
            #     f"{fn_parsed} is older than {fn_input}, "
            #     + "running Stanford Parser..."
            # )
            subprocess.run(cmd, shell=True, capture_output=True)
        # else:
        #     print(f"{fn_parsed} is newer than {fn_input}, parsing is skipped.")

    def _query(self, pattern: str, fn_parsed: str):
        """
        Call Tregex to query {pattern} against {fn_parsed}

        :param pattern: Tregex pattern
        :param fn_parsed: parsed file by Stanford Parser
        :return (int) frequency: frequency of the pattern
        :return (str) matched_subtreees: matched subtrees of the pattern
        """
        method = "edu.stanford.nlp.trees.tregex.TregexPattern"
        cmd = (
            "java -mx100m -cp"
            f" {self.classpath_tregex} {method} {pattern} {fn_parsed} -o"
        )
        p = subprocess.run(cmd, shell=True, capture_output=True)
        freq_match = re.search(
            r"There were (\d+) matches in total\.", p.stderr.decode()
        )
        if freq_match:
            freq = freq_match.group(1)
        else:
            os.remove(fn_parsed)
            # Make sure parsing will not be skipped on next running.
            sys.exit(
                "Error: failed to obtain frequency. It is likely that\n(1) Java"
                " is unavailable. Make sure you have Java 8 or later installed"
                " and can access it in the cmd window by typing in `java`.\n(2)"
                " You manually modified Tregex patterns in structures.py. Make"
                " sure that: on Windows, those patterns are enclosed by double"
                " quotes; on Linux and MacOS they are surrounded by single"
                " quotes.\n(3) Tregex's interface has changed. As a"
                " workaround, try an older version, v4.2.0, for example. The"
                " latest version of Tregex will be supported in next few"
                " releases."
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

    def _analyze_text(self, fn_input, is_reserve_parsed):
        """
        Analyze a text file

        :param fn_input: which file to analyze
        :param is_reserve_parsed: option to reserve Stanford Parser's
         parsing results
        :return structures: an instance of Structures
        """
        fn_parsed = path.splitext(fn_input)[0] + ".parsed"
        self._parse(fn_input, fn_parsed)

        structures = Structures(path.basename(fn_input))
        for structure in structures.to_search_for:
            print(
                f'\t[Tregex] Querying "{structure.desc}" against '
                f"{path.basename(fn_parsed)}..."
            )
            structure.freq, structure.matches = self._query(
                structure.pat, fn_parsed
            )
        structures.update_freqs()
        structures.W.freq = len(
            re.findall(r"\([A-Z]+\$? [^()]+\)", open(fn_parsed, "r").read())
        )
        structures.compute_SC_indicies()
        if not is_reserve_parsed:
            os.remove(fn_parsed)
        return structures

    def perform_analysis(self, fn_inputs: list, is_reserve_parsed: bool):
        """
        :param fn_inputs: list of input files
        :param is_reserve_parsed: option to reserve Stanford Parser's
         parsing results
        """
        total = len(fn_inputs)
        for i, fn_input in enumerate(fn_inputs):
            print(
                "[L2SCA] Processing"
                f" {path.basename(fn_input)} ({i+1}/{total})..."
            )
            structures = self._analyze_text(fn_input, is_reserve_parsed)
            yield structures
