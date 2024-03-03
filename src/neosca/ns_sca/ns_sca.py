#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import sys
from typing import Dict, List, Optional, Set, Tuple, Union

from neosca.ns_io import Ns_Cache, Ns_IO
from neosca.ns_sca.structure_counter import StructureCounter
from neosca.ns_utils import Ns_Procedure_Result


class Ns_SCA:
    def __init__(  # {{{
        self,
        ofile_freq: str = "result.csv",
        oformat_freq: str = "csv",
        odir_matched: str = "",
        selected_measures: Optional[List[str]] = None,
        precision: int = 4,
        is_cache: bool = True,
        is_use_cache: bool = True,
        is_stdout: bool = False,
        is_skip_parsing: bool = False,
        is_save_matches: bool = False,
        is_save_values: bool = True,
        config: Optional[str] = None,
    ) -> None:
        self.ofile_freq = ofile_freq
        self.oformat_freq = oformat_freq
        self.odir_matched = odir_matched
        self.selected_measures = selected_measures
        self.precision = precision
        self.is_cache = is_cache
        self.is_use_cache = is_use_cache
        self.is_stdout = is_stdout
        self.is_skip_parsing = is_skip_parsing
        self.is_save_matches = is_save_matches
        self.is_save_values = is_save_values

        self.user_data, self.user_structure_defs, self.user_snames = self.load_user_config(config)
        logging.debug(f"User defined snames: {self.user_snames}")

        if selected_measures is not None:
            StructureCounter.check_undefined_measure(selected_measures, self.user_snames)

        self.counters: List[StructureCounter] = []

    # }}}
    def load_user_config(self, config: Optional[str]) -> Tuple[dict, List[dict], Optional[Set[str]]]:  # {{{
        user_data: dict = {}
        user_structure_defs: List[Dict[str, str]] = []
        user_snames: Optional[Set[str]] = None

        if config is not None:
            user_data = Ns_IO.load_json(config)
            user_structure_defs = user_data["structures"]
            user_snames = StructureCounter.check_user_structure_def(user_structure_defs)

        return user_data, user_structure_defs, user_snames

    # }}}
    def get_forest_frm_text(self, text: str, cache_path: Optional[str] = None) -> str:  # {{{
        if self.is_skip_parsing:  # Assume input as parse trees
            return text

        from neosca.ns_nlp import Ns_NLP_Stanza

        forest = Ns_NLP_Stanza.get_constituency_forest(text, cache_path=cache_path)
        return forest

    # }}}
    def get_forest_frm_file(self, file_path: str) -> str:  # {{{
        from stanza import Document

        from neosca.ns_nlp import Ns_NLP_Stanza

        if self.is_skip_parsing:
            # Assume input as parse trees, e.g., (ROOT (S (NP) (VP)))
            return Ns_IO.load_file(file_path)

        cache_path, is_cache_available = Ns_Cache.get_cache_path(file_path)
        # Use cache
        if self.is_use_cache and is_cache_available:
            logging.info(f"Loading cache: {cache_path}.")
            doc: Document = Ns_NLP_Stanza.serialized2doc(Ns_IO.load_lzma(cache_path))
            return Ns_NLP_Stanza.get_constituency_forest(doc, cache_path=cache_path)

        # Use raw text
        text = Ns_IO.load_file(file_path)

        if not self.is_cache:
            cache_path = None

        try:
            forest = self.get_forest_frm_text(text, cache_path)
        except BaseException as e:
            # If cache is generated at current run, remove it as it is potentially broken
            if cache_path is not None and os_path.exists(cache_path) and not is_cache_available:
                os.remove(cache_path)
            raise e
        else:
            return forest

    # }}}
    def run_on_text(self, text: str, *, file_path: str = "cli_text", clear: bool = True) -> None:  # {{{
        if clear:
            self.counters.clear()

        forest: str = self.get_forest_frm_text(text)
        counter = StructureCounter(
            file_path,
            selected_measures=self.selected_measures,
            user_structure_defs=self.user_structure_defs,
        )
        counter.determine_all_values(forest)
        self.counters.append(counter)

        if self.is_save_matches:
            self.dump_matches()
        if self.is_save_values:
            self.dump_values()

    # }}}
    def run_on_file_or_subfiles(  # {{{
        self, file_or_subfiles: Union[str, List[str]]
    ) -> StructureCounter:
        if isinstance(file_or_subfiles, str):
            file_path = file_or_subfiles
            # Parse
            forest = self.get_forest_frm_file(file_path)
            counter = StructureCounter(
                file_path,
                selected_measures=self.selected_measures,
                user_structure_defs=self.user_structure_defs,
            )
            # Query
            counter.determine_all_values(forest)
        elif isinstance(file_or_subfiles, list):
            subfiles = file_or_subfiles
            total = len(subfiles)
            counter = StructureCounter(
                selected_measures=self.selected_measures,
                user_structure_defs=self.user_structure_defs,
            )
            # Merge measures defined by tregex_pattern
            for i, subfile in enumerate(subfiles, 1):
                logging.info(f'Processing "{subfile}" ({i}/{total})...')
                child_counter = self.run_on_file_or_subfiles(subfile)
                counter += child_counter
        else:
            raise ValueError(f"file_or_subfiles {file_or_subfiles} is neither str nor list")
        return counter

    # }}}
    def run_on_file_or_subfiles_list(  # {{{
        self, file_or_subfiles_list: List[Union[str, List[str]]], *, clear: bool = True
    ) -> None:
        if clear:
            self.counters.clear()

        for file_or_subfiles in file_or_subfiles_list:
            counter = self.run_on_file_or_subfiles(file_or_subfiles)
            self.counters.append(counter)

        if self.is_save_matches:
            self.dump_matches()
        if self.is_save_values:
            self.dump_values()

    # }}}
    def dump_matches(self) -> None:  # {{{
        for counter in self.counters:
            counter.dump_matches(self.odir_matched, self.is_stdout)

    # }}}
    def dump_values(self) -> None:  # {{{
        logging.debug("Writting counts and/or frequencies...")

        if len(self.counters) == 0:
            raise ValueError("empty counter list")


        sname_value_maps: List[Dict[str, str]] = [
            counter.get_all_values(self.precision) for counter in self.counters
        ]

        handle = sys.stdout if self.is_stdout else open(self.ofile_freq, "w", encoding="utf-8", newline="")  # noqa: SIM115

        if self.oformat_freq == "csv":
            import csv

            fieldnames = sname_value_maps[0].keys()
            csv_writer = csv.DictWriter(handle, fieldnames=fieldnames)

            csv_writer.writeheader()
            csv_writer.writerows(sname_value_maps)

        elif self.oformat_freq == "json":
            import json

            json.dump(sname_value_maps, handle, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f'oformat_freq {self.oformat_freq} not in ("csv", "json")')

        handle.close()
        # }}}

    @classmethod
    def list_fields(cls) -> Ns_Procedure_Result:
        counter = StructureCounter()
        for s_name in counter.selected_measures:
            print(f"{s_name}: {counter.get_structure(s_name).description}")
        return True, None
