import logging
import os
import sys
from typing import Dict, List, Optional, Set

from .io import SCAIO
from .parser import StanfordParser
from .querier import StanfordTregex
from .structure_counter import StructureCounter
from .util_env import unite_classpaths


class NeoSCA:
    def __init__(
        self,
        ofile_freq: str = "result.csv",
        oformat_freq: str = "csv",
        stanford_parser_home: str = "",
        stanford_tregex_home: str = "",
        odir_matched: str = "",
        newline_break: str = "never",
        max_length: Optional[int] = None,
        selected_measures: Optional[Set[str]] = None,
        is_reserve_parsed: bool = False,
        is_reserve_matched: bool = False,
        is_stdout: bool = False,
        is_skip_querying: bool = False,
        is_skip_parsing: bool = False,
        is_pretokenized: bool = False,
        is_verbose: bool = True,
    ) -> None:
        self.ofile_freq = ofile_freq
        self.oformat_freq = oformat_freq
        self.classpaths = unite_classpaths(stanford_parser_home, stanford_tregex_home)
        self.odir_matched = odir_matched
        self.newline_break = newline_break
        self.max_length = max_length
        self.selected_measures = selected_measures
        self.is_reserve_parsed = is_reserve_parsed
        self.is_reserve_matched = is_reserve_matched
        self.is_stdout = is_stdout
        self.is_skip_querying = is_skip_querying
        self.is_skip_parsing = is_skip_parsing
        self.is_pretokenized = is_pretokenized
        self.is_verbose = is_verbose
        self.counter_lists: List[StructureCounter] = []
        self.io = SCAIO()

        self.is_stanford_parser_initialized = False
        self.is_stanford_tregex_initialized = False

    def ensure_stanford_tregex_initialized(self) -> None:
        if not self.is_stanford_tregex_initialized:
            self.tregex = StanfordTregex(classpaths=self.classpaths)
            self.is_stanford_tregex_initialized = True

    def ensure_stanford_parser_initialized(self) -> None:
        if not self.is_stanford_parser_initialized:
            self.parser = StanfordParser(
                classpaths=self.classpaths,
                is_verbose=self.is_verbose,
            )
            self.is_stanford_parser_initialized = True

    def has_parse_file(self, ofile_parsed: str, ifile: str) -> bool:
        """Check is a parse file already exists before parsing"""
        has_parse_file = False
        is_exist = os.path.exists(ofile_parsed)
        if is_exist:
            is_not_empty = os.path.getsize(ofile_parsed) > 0
            is_parsed_newer_than_input = os.path.getmtime(ofile_parsed) > os.path.getmtime(ifile)
            if is_not_empty and is_parsed_newer_than_input:
                has_parse_file = True
        return has_parse_file

    def query_against_trees(self, trees: str, counter: StructureCounter) -> StructureCounter:
        self.ensure_stanford_tregex_initialized()
        counter = self.tregex.query(
            counter,
            trees,
            is_reserve_matched=self.is_reserve_matched,
            odir_matched=self.odir_matched,
            is_stdout=self.is_stdout,
        )
        return counter

    def parse_text(self, text: str, ofile_parsed="cmdline_text.parsed") -> str:
        if self.is_skip_parsing:  # assume input as parse trees
            return text

        self.ensure_stanford_parser_initialized()
        trees = self.parser.parse(
            text,
            max_length=self.max_length,
            newline_break=self.newline_break,
            is_pretokenized=self.is_pretokenized,
            is_reserve_parsed=self.is_reserve_parsed,
            ofile_parsed=ofile_parsed,
            is_stdout=self.is_stdout,
        )
        return trees

    def run_on_text(self, text: str, ifile: str = "cmdline_text") -> None:
        trees: str = self.parse_text(text)
        if not self.is_skip_querying:
            counter = StructureCounter(ifile, selected_measures=self.selected_measures)
            counter = self.query_against_trees(trees, counter)
            self.counter_lists.append(counter)
            self.write_freq_output()

    def parse_ifile(self, ifile: str) -> str:
        """Parse a single file"""
        if self.is_skip_parsing:
            # assume input as parse trees
            return self.io.read_txt(ifile, is_guess_encoding=False)

        ofile_parsed = os.path.splitext(ifile)[0] + ".parsed"
        has_parse_file = self.has_parse_file(ofile_parsed=ofile_parsed, ifile=ifile)
        if has_parse_file:
            logging.info(
                f"[Parser] Parsing skipped: {ofile_parsed} already"
                f" exists, and is non-empty and newer than {ifile}."
            )
            # parse file are always (1) plain text, and (2) of utf-8 encoding
            return self.io.read_txt(ofile_parsed, is_guess_encoding=False)
        text = self.io.read_file(ifile)
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
        if not ifiles:
            return None
        total = len(ifiles)
        if not self.is_skip_querying:
            if is_combine:
                parent_counter = StructureCounter(selected_measures=self.selected_measures)
                for i, ifile in enumerate(ifiles, 1):
                    logging.info(f'[NeoSCA] Processing "{ifile}" ({i}/{total})...')
                    child_counter = self.parse_ifile_and_query(ifile)
                    parent_counter += child_counter
                self.counter_lists.append(parent_counter)
            else:
                for i, ifile in enumerate(ifiles, 1):
                    logging.info(f'[NeoSCA] Processing "{ifile}" ({i}/{total})...')
                    counter = self.parse_ifile_and_query(ifile)
                    self.counter_lists.append(counter)
            self.write_freq_output()
        else:
            for i, ifile in enumerate(ifiles, 1):
                logging.info(f'[NeoSCA] Processing "{ifile}" ({i}/{total})...')
                self.parse_ifile(ifile)

    def get_freq_output(self, format_: str) -> str:
        assert format_ in ("csv", "json")
        if format_ == "csv":
            freq_output = self.counter_lists[0].fields
            for counter in self.counter_lists:
                freq_dict = counter.get_all_freqs()
                if "," in freq_dict["Filename"]:
                    freq_dict["Filename"] = '"' + freq_dict["Filename"] + '"'
                freq_output += "\n" + ",".join(str(freq) for freq in freq_dict.values())
        else:
            import json

            final_freq_dict: Dict[str, List[Dict]] = {"Files": []}
            for counter in self.counter_lists:
                freq_dict = counter.get_all_freqs()
                final_freq_dict["Files"].append(freq_dict)
            freq_output = json.dumps(final_freq_dict)
        return freq_output

    def write_freq_output(self) -> None:
        freq_output = self.get_freq_output(self.oformat_freq)
        if not self.is_stdout:
            with open(self.ofile_freq, "w", encoding="utf-8") as f:
                f.write(freq_output)
        else:
            sys.stdout.write(freq_output + "\n")
