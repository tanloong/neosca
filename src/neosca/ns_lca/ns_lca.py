#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import sys
from typing import Dict, List, Literal, Optional, Tuple, Union

from neosca.ns_io import Ns_Cache, Ns_IO
from neosca.ns_lca.ns_lca_counter import Ns_LCA_Counter
from neosca.ns_utils import Ns_Procedure_Result


class Ns_LCA:
    def __init__(
        self,
        wordlist: str = "bnc",
        tagset: Literal["ud", "ptb"] = "ud",
        easy_word_threshold: int = 2000,
        section_size: int = 50,
        ndw_trials: int = 10,
        precision: int = 4,
        ofile_freq: str = "result.csv",
        oformat_freq: str = "csv",
        odir_matched: str = "",
        is_cache: bool = True,
        is_use_cache: bool = True,
        is_stdout: bool = False,
        is_save_matches: bool = False,
        is_save_values: bool = True,
    ) -> None:
        assert wordlist in ("bnc", "anc")
        assert tagset in ("ud", "ptb")
        logging.debug(f"Using {wordlist.upper()} wordlist")
        self.wordlist = wordlist
        logging.debug(f"Using {tagset.upper()} POS tagset")
        assert tagset in ("ud", "ptb")
        self.tagset: Literal["ud", "ptb"] = tagset

        self.easy_word_threshold = easy_word_threshold
        self.section_size = section_size
        self.ndw_trials = ndw_trials
        self.precision = precision
        self.ofile_freq = ofile_freq
        self.oformat_freq = oformat_freq
        self.odir_matched = odir_matched
        self.is_stdout = is_stdout
        self.is_cache = is_cache
        self.is_use_cache = is_use_cache
        self.is_save_matches = is_save_matches
        self.is_save_values = is_save_values

        self.counters: List[Ns_LCA_Counter] = []

    def get_lempos_frm_text(
        self, text: str, /, cache_path: Optional[str] = None
    ) -> Tuple[Tuple[str, str], ...]:
        from neosca.ns_nlp import Ns_NLP_Stanza

        return Ns_NLP_Stanza.get_lemma_and_pos(text, tagset=self.tagset, cache_path=cache_path)

    def get_lempos_frm_file(self, file_path: str, /) -> Tuple[Tuple[str, str], ...]:
        from neosca.ns_nlp import Ns_NLP_Stanza

        cache_path, is_cache_available = Ns_Cache.get_cache_path(file_path)
        # Use cache
        if self.is_use_cache and is_cache_available:
            logging.info(f"Loading cache: {cache_path}.")
            doc = Ns_NLP_Stanza.serialized2doc(Ns_IO.load_lzma(cache_path))
            return Ns_NLP_Stanza.get_lemma_and_pos(doc, tagset=self.tagset, cache_path=cache_path)

        # Use raw text
        text = Ns_IO.load_file(file_path)

        if not self.is_cache:
            cache_path = None

        try:
            return self.get_lempos_frm_text(text)
        except BaseException as e:
            # If cache is generated at current run, remove it as it is potentially broken
            if cache_path is not None and os_path.exists(cache_path) and not is_cache_available:
                os.remove(cache_path)
            raise e

    def init_new_counter(self, file_path: str = "") -> Ns_LCA_Counter:
        return Ns_LCA_Counter(
            file_path,
            wordlist=self.wordlist,
            tagset=self.tagset,
            easy_word_threshold=self.easy_word_threshold,
            section_size=self.section_size,
            ndw_trials=self.ndw_trials,
        )

    def run_on_text(self, text: str, *, file_path: str = "cli_text", clear: bool = True) -> None:
        if clear:
            self.counters.clear()

        lempos_tuples = self.get_lempos_frm_text(text)
        counter = self.init_new_counter(file_path)
        counter.determine_all_values(lempos_tuples)
        self.counters.append(counter)

        if self.is_save_matches:
            self.dump_matches()
        if self.is_save_values:
            self.dump_values()

    def run_on_file_or_subfiles(self, file_or_subfiles: Union[str, List[str]]) -> Ns_LCA_Counter:
        if isinstance(file_or_subfiles, str):
            file_path = file_or_subfiles
            lempos_tuples = self.get_lempos_frm_file(file_path)
            counter = self.init_new_counter(file_path)
            counter.determine_all_values(lempos_tuples)
        elif isinstance(file_or_subfiles, list):
            subfiles = file_or_subfiles
            total = len(subfiles)
            counter = self.init_new_counter()
            for i, subfile in enumerate(subfiles, 1):
                logging.info(f'Processing "{subfile}" ({i}/{total})...')
                child_counter = self.run_on_file_or_subfiles(subfile)
                counter += child_counter
        else:
            raise ValueError(f"file_or_subfiles {file_or_subfiles} is neither str nor list")
        return counter

    def run_on_file_or_subfiles_list(
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

    def dump_values(self) -> None:
        logging.debug("Writting counts and/or frequencies...")

        if len(self.counters) == 0:
            raise ValueError("empty counter list")

        value_tables: List[Dict[str, str]] = [
            counter.get_all_values(self.precision) for counter in self.counters
        ]

        handle = sys.stdout if self.is_stdout else open(self.ofile_freq, "w", encoding="utf-8", newline="")  # noqa: SIM115

        if self.oformat_freq == "csv":
            import csv

            fieldnames = value_tables[0].keys()
            csv_writer = csv.DictWriter(handle, fieldnames=fieldnames)

            csv_writer.writeheader()
            csv_writer.writerows(value_tables)
        elif self.oformat_freq == "json":
            import json

            json.dump(value_tables, handle, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f'oformat_freq {self.oformat_freq} not in ("csv", "json")')

        handle.close()

    def dump_matches(self) -> None:
        for counter in self.counters:
            counter.dump_matches(self.odir_matched, self.is_stdout)

    @classmethod
    def list_fields(cls) -> Ns_Procedure_Result:
        for short, long in Ns_LCA_Counter.COUNT_ITEMS.items():
            for suffix in ("types", "tokens"):
                print(f"{short}{suffix}: {long} {suffix}")
        for short, long in Ns_LCA_Counter.FREQ_ITEMS.items():
            print(f"{short}: {long}")
        return True, None
