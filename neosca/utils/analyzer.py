import os
from os import path
import re
import subprocess
import sys
from typing import Tuple, Generator

from .structures import Structures


class Analyzer:
    method_parser = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
    model_parser = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
    method_tregex = "edu.stanford.nlp.trees.tregex.TregexPattern"

    def __init__(self, dir_stanford_parser, dir_stanford_tregex):
        """
        :param dir_parser: directory to Stanford Parser
        :param dir_tregex: directory to Tregex
        """
        self.classpath_parser = '"' + dir_stanford_parser + os.sep + "*" + '"'
        self.classpath_tregex = (
            '"' + dir_stanford_tregex + os.sep + "stanford-tregex.jar" + '"'
        )

    def _parse(self, ifile: str, fn_parsed: str) -> None:
        """
        Call Stanford Parser

        :param ifile: file to parse
        :param fn_parsed: where to save the parsed results
        :return: None
        """
        cmd = (
            f"java -mx1500m -cp {self.classpath_parser} {self.method_parser} "
            f"-outputFormat penn {self.model_parser} {ifile} > {fn_parsed}"
        )
        if not path.exists(fn_parsed):
            # print(f"{fn_parsed} does not exist, running Stanford Parser...")
            subprocess.run(cmd, shell=True, capture_output=True)
            return
        mt_input = path.getmtime(ifile)  # get the last modification time
        mt_parsed = path.getmtime(fn_parsed)
        if mt_input > mt_parsed:
            # print(
            #     f"{fn_parsed} is older than {ifile}, "
            #     + "running Stanford Parser..."
            # )
            subprocess.run(cmd, shell=True, capture_output=True)
        # else:
        #     print(f"{fn_parsed} is newer than {ifile}, parsing is skipped.")

    def _query(self, pattern: str, fn_parsed: str) -> Tuple[int, str]:
        """
        Call Tregex to query {pattern} against {fn_parsed}

        :param pattern: Tregex pattern
        :param fn_parsed: parsed file by Stanford Parser
        :return (int) frequency: frequency of the pattern
        :return (str) matched_subtreees: matched subtrees of the pattern
        """
        cmd = (
            "java -mx100m -cp"
            f" {self.classpath_tregex} {self.method_tregex} {pattern} {fn_parsed} -o"
        )
        p = subprocess.run(cmd, shell=True, capture_output=True)
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

    def _analyze_text(self, ifile, reserve_parsed) -> Structures:
        """
        Analyze a text file

        :param ifile: which file to analyze
        :param reserve_parsed: option to reserve Stanford Parser's
         parsing results
        :return structures: an instance of Structures
        """
        fn_parsed = path.splitext(ifile)[0] + ".parsed"
        self._parse(ifile, fn_parsed)

        structures = Structures(path.basename(ifile))
        for structure in structures.to_search_for:
            print(
                f'\t[Tregex] Querying "{structure.desc}" against '
                f"{path.basename(fn_parsed)}..."
            )
            structure.freq, structure.matches = self._query(
                structure.pat, fn_parsed
            )
        structures.update_freqs()

        with open(fn_parsed, "r", encoding="utf-8") as f:
            structures.W.freq = len(
                re.findall(r"\([A-Z]+\$? [^()]+\)", f.read())
            )

        structures.compute_SC_indicies()
        if not reserve_parsed:
            os.remove(fn_parsed)
        return structures

    def perform_analysis(
        self, ifiles: list, reserve_parsed: bool
    ) -> Generator[Structures, None, None]:
        """
        :param ifiles: list of input files
        :param reserve_parsed: option to reserve Stanford Parser's
         parsing results
        """
        total = len(ifiles)
        for i, ifile in enumerate(ifiles):
            print(
                f"[NeoSCA] Processing {path.basename(ifile)} ({i+1}/{total})..."
            )
            structures = self._analyze_text(ifile, reserve_parsed)
            yield structures
