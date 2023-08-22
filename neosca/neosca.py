import json
import logging
import os
import os.path as os_path
import sys
from typing import Dict, List, Optional, Set, Tuple

from .parser import StanfordParser
from .querier import StanfordTregex
from .scaenv import unite_classpaths
from .scaio import SCAIO
from .structure_counter import StructureCounter


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
        selected_measures: Optional[List[str]] = None,
        is_reserve_parsed: bool = False,
        is_reserve_matched: bool = False,
        is_stdout: bool = False,
        is_skip_querying: bool = False,
        is_skip_parsing: bool = False,
        is_pretokenized: bool = False,
        config: Optional[str] = None,
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

        self.user_data, self.user_structure_defs, self.user_snames = self.load_user_config(
            config
        )
        logging.debug(f"[NeoSCA] user_snames: {self.user_snames}")

        if selected_measures is not None:
            StructureCounter.check_undefined_measure(selected_measures, self.user_snames)

        self.counters: List[StructureCounter] = []
        self.io = SCAIO()
        self.is_stanford_parser_initialized = False
        self.is_stanford_tregex_initialized = False

    def load_user_config(
        self, config: Optional[str]
    ) -> Tuple[dict, List[dict], Optional[Set[str]]]:
        user_data: dict = {}
        user_structure_defs: List[Dict[str, str]] = []
        user_snames: Optional[Set[str]] = None

        if config is not None:
            with open(config, "r", encoding="utf-8") as f:
                user_data = json.load(f)

            user_structure_defs = user_data["structures"]
            user_snames = StructureCounter.check_user_structure_def(user_structure_defs)

        return user_data, user_structure_defs, user_snames

    def ensure_stanford_tregex_initialized(self) -> None:
        if not self.is_stanford_tregex_initialized:
            self.tregex = StanfordTregex(classpaths=self.classpaths)
            self.is_stanford_tregex_initialized = True

    def ensure_stanford_parser_initialized(self) -> None:
        if not self.is_stanford_parser_initialized:
            self.parser = StanfordParser(classpaths=self.classpaths)
            self.is_stanford_parser_initialized = True

    def already_parsed(self, ofile_parsed: str, ifile: str) -> bool:
        has_been_parsed = False
        is_exist = os_path.exists(ofile_parsed)
        if is_exist:
            is_not_empty = os_path.getsize(ofile_parsed) > 0
            is_parsed_newer_than_input = os_path.getmtime(ofile_parsed) > os_path.getmtime(ifile)
            if is_not_empty and is_parsed_newer_than_input:
                has_been_parsed = True
        return has_been_parsed

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

    def parse_ifile(self, ifile: str) -> Optional[str]:
        if self.is_skip_parsing:
            # assume input as parse trees
            return self.io.read_txt(ifile, is_guess_encoding=False)

        ofile_parsed = os_path.splitext(ifile)[0] + ".parsed"
        has_been_parsed = self.already_parsed(ofile_parsed=ofile_parsed, ifile=ifile)
        if has_been_parsed:
            logging.info(
                f"Parsing skipped: {ofile_parsed} already"
                f" exists, and is non-empty and newer than {ifile}."
            )
            # parse file are always (1) plain text, and (2) of utf-8 encoding
            return self.io.read_txt(ofile_parsed, is_guess_encoding=False)

        text = self.io.read_file(ifile)
        if text is None:
            return None

        try:
            trees = self.parse_text(text, ofile_parsed)
        except KeyboardInterrupt:
            if os_path.exists(ofile_parsed):
                os.remove(ofile_parsed)
            sys.exit(1)
        else:
            return trees

    def run_on_text(self, text: str, ifile: str = "cmdline_text") -> None:
        trees: str = self.parse_text(text)

        if self.is_skip_querying:
            return

        counter = StructureCounter(
            ifile,
            selected_measures=self.selected_measures,
            user_structure_defs=self.user_structure_defs,
        )
        counter = self.query_against_trees(trees, counter)
        self.counters.append(counter)
        self.write_value_output()

    def parse_and_query_ifile(self, ifile: str) -> Optional[StructureCounter]:
        trees = self.parse_ifile(ifile)
        if trees is None:
            return None

        counter = StructureCounter(
            ifile,
            selected_measures=self.selected_measures,
            user_structure_defs=self.user_structure_defs,
        )
        return self.query_against_trees(trees, counter)

    def parse_ifiles(self, ifiles: List[str]):
        total = len(ifiles)
        for i, ifile in enumerate(ifiles, 1):
            logging.info(f'[NeoSCA] Processing "{ifile}" ({i}/{total})...')
            self.parse_ifile(ifile)

    def parse_subfiles_list(self, subfiles_list: List[List[str]]):
        for subfiles in subfiles_list:
            self.parse_ifiles(subfiles)

    def parse_and_query_ifiles(self, ifiles):
        total = len(ifiles)
        for i, ifile in enumerate(ifiles, 1):
            logging.info(f'[NeoSCA] Processing "{ifile}" ({i}/{total})...')
            counter = self.parse_and_query_ifile(ifile)
            if counter is None:
                continue
            self.counters.append(counter)

    def parse_and_query_subfiles_list(self, subfiles_list: List[List[str]]):
        for subfiles in subfiles_list:
            total = len(subfiles)
            parent_counter = StructureCounter(
                selected_measures=self.selected_measures,
                user_structure_defs=self.user_structure_defs,
            )

            for i, subfile in enumerate(subfiles, 1):
                logging.info(f'[NeoSCA] Processing "{subfile}" ({i}/{total})...')
                child_counter = self.parse_and_query_ifile(subfile)
                if child_counter is None:
                    continue
                parent_counter += child_counter

            self.tregex.set_all_values(parent_counter, "")
            self.counters.append(parent_counter)

    def run_on_ifiles(self, files: List[str] = [], subfiles_list: List[List[str]] = []) -> None:
        if self.is_skip_querying:
            self.parse_ifiles(files)
            self.parse_subfiles_list(subfiles_list)
            return

        self.parse_and_query_ifiles(files)
        self.parse_and_query_subfiles_list(subfiles_list)
        self.write_value_output()

    def write_value_output(self) -> None:
        logging.debug("[NeoSCA] Writting counts and/or frequencies...")

        counters = self.counters
        if len(counters) == 0:
            raise ValueError("empty counter list")

        oformat_freq = self.oformat_freq
        if oformat_freq not in ("csv", "json"):
            raise ValueError(f'oformat_freq {oformat_freq} not in ("csv", "json")')

        sname_value_maps: List[Dict[str, str]] = [
            counter.get_all_values() for counter in counters
        ]

        handle = (
            open(self.ofile_freq, "w", encoding="utf-8", newline="")
            if not self.is_stdout
            else sys.stdout
        )

        if oformat_freq == "csv":
            import csv

            fieldnames = sname_value_maps[0].keys()
            writer = csv.DictWriter(handle, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(sname_value_maps)

        else:
            import json

            json.dump(sname_value_maps, handle)

        handle.close()
