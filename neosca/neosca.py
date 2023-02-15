import os
import re
import sys
from typing import List, Dict

from .parser import StanfordParser
from .querier import StanfordTregex
from .structures import Structures


class NeoSCA:
    def __init__(
        self,
        ofile_freq,  # str or sys.stdout
        oformat_freq: str,
        dir_stanford_parser: str,
        dir_stanford_tregex: str,
        reserve_parsed: bool,
        reserve_matched: bool,
        odir_matched: str,
        newline_break: str,
        max_length: int,
        is_skip_querying: bool,
        verbose: bool = True,
    ) -> None:
        self.ofile_freq = ofile_freq
        self.oformat_freq = oformat_freq
        self.dir_stanford_parser = dir_stanford_parser
        self.dir_stanford_tregex = dir_stanford_tregex
        self.reserve_parsed = reserve_parsed
        self.reserve_matched = reserve_matched
        self.odir_matched = odir_matched
        self.newline_break = newline_break
        self.max_length = max_length
        self.is_skip_querying = is_skip_querying
        self.verbose = verbose
        self.structures_lists: List[Structures] = []

        self.parser = StanfordParser(
            self.dir_stanford_parser,
            verbose=self.verbose,
            newline_break=self.newline_break,
            max_length=max_length,
        )
        self.tregex = StanfordTregex(
            dir_stanford_tregex=self.dir_stanford_tregex,
            reserve_matched=self.reserve_matched,
            odir_matched=self.odir_matched,
        )

    def _is_skip_parsing(self, ofile_parsed: str, ifile: str) -> bool:
        """See whether a parsed file already exists"""
        is_skip_parsing = False
        is_exist = os.path.exists(ofile_parsed)
        if is_exist:
            is_not_empty = os.path.getsize(ofile_parsed) > 0
            is_parsed_newer_than_input = os.path.getmtime(ofile_parsed) > os.path.getmtime(ifile)
            if is_not_empty and is_parsed_newer_than_input:
                is_skip_parsing = True
        return is_skip_parsing

    def _read_file(self, filename: str) -> str:
        """Read a file (either an input file or a parsed file) and return the content"""
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def query_against_trees(self, trees: str, structures: Structures) -> Structures:
        structures = self.tregex.query(structures, trees)
        structures.W.freq = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
        structures.update_freqs()
        structures.compute_14_indicies()
        return structures

    def parse_text(self, text: str, ofile_parsed="cmdline_text.parsed") -> str:
        trees = self.parser.parse(text)
        if self.reserve_parsed:
            with open(ofile_parsed, "w", encoding="utf-8") as f:
                f.write(trees)
        return trees

    def run_on_text(self, text: str, ifile: str = "cmdline_text") -> None:
        trees = self.parse_text(text)
        if not self.is_skip_querying:
            structures = Structures(ifile)
            structures = self.query_against_trees(trees, structures)
            self.structures_lists.append(structures)
        if not self.is_skip_querying:
            self.write_freq_output()

    def parse_ifile(self, ifile: str) -> str:
        """Parse a single file"""
        ofile_parsed = os.path.splitext(ifile)[0] + ".parsed"
        is_skip_parsing = self._is_skip_parsing(ofile_parsed=ofile_parsed, ifile=ifile)
        if is_skip_parsing:
            print(
                f"\t[Parser] Parsing skipped: {ofile_parsed} already"
                f" exists, and is non-empty and newer than {ifile}."
            )
            return self._read_file(ofile_parsed)
        text = self._read_file(ifile)
        try:
            trees = self.parse_text(text, ofile_parsed)
        except KeyboardInterrupt:
            if os.path.exists(ofile_parsed):
                os.remove(ofile_parsed)
            sys.exit(1)
        else:
            return trees

    def parse_ifile_and_query(self, ifile: str, idx: int, total: int) -> Structures:
        print(f'[NeoSCA] Processing "{ifile}" ({idx+1}/{total})...')
        trees = self.parse_ifile(ifile)
        structures = Structures(ifile)
        return self.query_against_trees(trees, structures)

    def run_on_ifiles(self, ifiles, is_combine=False) -> None:
        total = len(ifiles)
        if not self.is_skip_querying:
            if is_combine:
                parent_structures = Structures(ifile=None)
                for i, ifile in enumerate(ifiles):
                    structures = self.parse_ifile_and_query(ifile, i, total)
                    parent_structures += structures
                parent_structures.update_freqs()
                parent_structures.compute_14_indicies()
                self.structures_lists.append(parent_structures)
            else:
                for i, ifile in enumerate(ifiles):
                    structures = self.parse_ifile_and_query(ifile, i, total)
                    self.structures_lists.append(structures)
            self.write_freq_output()

    def write_freq_output(self) -> None:
        if self.oformat_freq == "csv":
            freq_output = Structures("").fields
            for structures in self.structures_lists:
                freq_dict = structures.get_freqs()
                freq_output += "\n" + ",".join(str(freq) for freq in freq_dict.values())
        elif self.oformat_freq == "json":
            import json

            final_freq_dict: Dict[str, List[Dict]] = {"Files": []}
            for structures in self.structures_lists:
                freq_dict = structures.get_freqs()
                final_freq_dict["Files"].append(freq_dict)
            freq_output = json.dumps(final_freq_dict)
        else:
            print(f"Unexpected output format: {self.oformat_freq}")
            sys.exit(1)

        if self.ofile_freq is not sys.stdout:
            with open(self.ofile_freq, "w", encoding="utf-8") as f:
                f.write(freq_output)
        else:
            self.ofile_freq.write(freq_output)
