import os
import sys
from typing import Dict, List, Optional, Set

from .parser import StanfordParser
from .querier import StanfordTregex
from .structure_counter import StructureCounter


class NeoSCA:
    def __init__(
        self,
        ofile_freq: str = "result.csv",
        oformat_freq: str = "csv",
        dir_stanford_parser: str = "",
        dir_stanford_tregex: str = "",
        odir_matched: str = "",
        newline_break: str = "never",
        max_length: Optional[int] = None,
        selected_measures: Optional[Set[str]] = None,
        is_reserve_parsed: bool = False,
        is_reserve_matched: bool = False,
        is_stdout: bool = False,
        is_skip_querying: bool = False,
        is_verbose: bool = True,
    ) -> None:
        self.ofile_freq = ofile_freq
        self.oformat_freq = oformat_freq
        self.dir_stanford_parser = dir_stanford_parser
        self.dir_stanford_tregex = dir_stanford_tregex
        self.odir_matched = odir_matched
        self.newline_break = newline_break
        self.max_length = max_length
        self.selected_measures = selected_measures
        self.is_reserve_parsed = is_reserve_parsed
        self.is_reserve_matched = is_reserve_matched
        self.is_stdout = is_stdout
        self.is_skip_querying = is_skip_querying
        self.is_verbose = is_verbose
        self.counter_lists: List[StructureCounter] = []

        self.parser = StanfordParser(
            self.dir_stanford_parser,
            is_verbose=self.is_verbose,
        )
        self.tregex = StanfordTregex(
            dir_stanford_tregex=self.dir_stanford_tregex,
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

    def query_against_trees(self, trees: str, counter: StructureCounter) -> StructureCounter:
        counter = self.tregex.query(
            counter,
            trees,
            is_reserve_matched=self.is_reserve_matched,
            odir_matched=self.odir_matched,
        )
        return counter

    def parse_text(self, text: str, ofile_parsed="cmdline_text.parsed") -> str:
        trees = self.parser.parse(text, self.max_length, self.newline_break)
        if self.is_reserve_parsed:
            with open(ofile_parsed, "w", encoding="utf-8") as f:
                f.write(trees)
        return trees

    def run_on_text(self, text: str, ifile: str = "cmdline_text") -> None:
        trees = self.parse_text(text)
        if not self.is_skip_querying:
            counter = StructureCounter(ifile, selected_measures=self.selected_measures)
            counter = self.query_against_trees(trees, counter)
            self.counter_lists.append(counter)
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

    def parse_ifile_and_query(self, ifile: str) -> StructureCounter:
        trees = self.parse_ifile(ifile)
        counter = StructureCounter(ifile, selected_measures=self.selected_measures)
        return self.query_against_trees(trees, counter)

    def run_on_ifiles(self, ifiles, is_combine=False) -> None:
        total = len(ifiles)
        if not self.is_skip_querying:
            if is_combine:
                parent_counter = StructureCounter(selected_measures=self.selected_measures)
                for i, ifile in enumerate(ifiles):
                    print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
                    child_counter = self.parse_ifile_and_query(ifile)
                    parent_counter += child_counter
                self.counter_lists.append(parent_counter)
            else:
                for i, ifile in enumerate(ifiles):
                    print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
                    child_counter = self.parse_ifile_and_query(ifile)
                    self.counter_lists.append(child_counter)
            self.write_freq_output()
        else:
            for i, ifile in enumerate(ifiles):
                print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
                self.parse_ifile(ifile)

    def write_freq_output(self) -> None:
        if self.oformat_freq == "csv":
            freq_output = StructureCounter(selected_measures=self.selected_measures).fields
            for structures in self.counter_lists:
                freq_dict = structures.get_freqs()
                freq_output += "\n" + ",".join(str(freq) for freq in freq_dict.values())
        elif self.oformat_freq == "json":
            import json

            final_freq_dict: Dict[str, List[Dict]] = {"Files": []}
            for structures in self.counter_lists:
                freq_dict = structures.get_freqs()
                final_freq_dict["Files"].append(freq_dict)
            freq_output = json.dumps(final_freq_dict)
        else:
            print(f"Unexpected output format: {self.oformat_freq}")
            sys.exit(1)

        if not self.is_stdout:
            with open(self.ofile_freq, "w", encoding="utf-8") as f:
                f.write(freq_output)
        else:
            sys.stdout.write(freq_output)
