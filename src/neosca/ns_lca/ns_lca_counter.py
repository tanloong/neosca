#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import random
import shutil
import sys
from math import log as _log
from math import sqrt as _sqrt
from typing import Dict, List, Literal, Optional, OrderedDict, Sequence, Tuple, Union

from neosca import DATA_DIR
from neosca.ns_io import Ns_IO
from neosca.ns_lca import word_classifiers
from neosca.ns_utils import chunks, safe_div


class Ns_LCA_Counter:
    WORDLIST_DATAFILE_MAP = {
        "bnc": "bnc_all_filtered.pickle.lzma",
        "anc": "anc_all_count.pickle.lzma",
    }
    COUNT_ITEMS = {
        "word": "word",
        "sword": "sophisticated word",
        "lex": "lexical word",
        "slex": "sophisticated lexical word",
        "verb": "verb",
        "sverb": "sophisticated verb",
        "adj": "adjective",
        "adv": "adverb",
        "noun": "noun",
    }
    FREQ_ITEMS = {
        "LD": "lexical density",
        "LS1": "lexical sophistication-I",
        "LS2": "lexical sophistication-II",
        "VS1": "verb sophistication-I",
        "VS2": "verb sophistication-II",
        "CVS1": "corrected VS1",
        "NDW": "number of different words",
        "NDW-50": "NDW in the first 50 words of sample",
        "NDW-ER50": "mean NDW of 10 random 50-word samples",
        "NDW-ES50": "mean NDW of 10 random 50-word sequences",
        "TTR": "type-token ratio",
        "MSTTR": "mean segmental TTR",
        "CTTR": "corrected TTR",
        "RTTR": "root TTR",
        "LogTTR": "bilogarithmic TTR",
        "Uber": "Uber index",
        "LV": "lexical word variation",
        "VV1": "verb variation-I",
        "SVV1": "squared VV1",
        "CVV1": "corrected VV1",
        "VV2": "verb variation-II",
        "NV": "noun variation",
        "AdjV": "adjective variation",
        "AdvV": "adverb variation",
        "ModV": "modifier variation",
    }
    DEFAULT_MEASURES: List[str] = [
        *(item + suffix for item in COUNT_ITEMS for suffix in ("types", "tokens")),
        *FREQ_ITEMS,
    ]

    def __init__(
        self,
        file_path: str = "",
        *,
        wordlist: str = "bnc",
        tagset: Literal["ud", "ptb"] = "ud",
        easy_word_threshold: int = 2000,
        section_size: int = 50,
        ndw_trials: int = 10,
    ) -> None:
        self.file_path = file_path

        self.count_table: Dict[str, List[str]] = {item: [] for item in self.COUNT_ITEMS}
        self.freq_table: Dict[str, Optional[Union[int, float]]] = {item: None for item in self.FREQ_ITEMS}

        word_data_path = DATA_DIR / self.WORDLIST_DATAFILE_MAP[wordlist]
        logging.debug(f"Loading {word_data_path}...")
        word_data = Ns_IO.load_pickle_lzma(word_data_path)
        self.word_classifier = {
            "ud": word_classifiers.Ns_UD_Word_Classifier,
            "ptb": word_classifiers.Ns_PTB_Word_Classifier,
        }[tagset](word_data=word_data, easy_word_threshold=easy_word_threshold)

        self.section_size = section_size
        self.ndw_trials = ndw_trials

    @classmethod
    def get_ndw_first_z(cls, lemma_sequence: Sequence[str], *, section_size: int):
        """NDW for first 'section_size' words in a sample"""
        if len(lemma_sequence) < section_size:
            return len(set(lemma_sequence))
        return len(set(lemma_sequence[:section_size]))

    @classmethod
    def get_ndw_erz(cls, lemma_sequence: Sequence[str], *, section_size: int, trials):
        """NDW expected random 'section_size' words, 10 trials by default"""
        if len(lemma_sequence) < section_size:
            return len(set(lemma_sequence))
        ndw_erz = 0
        for _ in range(trials):
            erz_lemma_lst = random.sample(lemma_sequence, section_size)

            ndw_erz_types = set(erz_lemma_lst)
            ndw_erz += len(ndw_erz_types)
        return ndw_erz / 10

    @classmethod
    def get_ndw_esz(cls, lemma_sequence: Sequence[str], *, section_size: int, trials):
        """NDW expected random sequences of 'section_size' words, 10 trials by default"""
        if len(lemma_sequence) < section_size:
            return len(set(lemma_sequence))
        ndw_esz = 0
        for _ in range(trials):
            start_word = random.randint(0, len(lemma_sequence) - section_size)
            esz_lemma_lst = lemma_sequence[start_word : start_word + section_size]

            ndw_esz_types = set(esz_lemma_lst)
            ndw_esz += len(ndw_esz_types)
        return ndw_esz / 10

    @classmethod
    def get_msttr(cls, lemma_sequence: Sequence[str], *, section_size: int):
        """
        Mean Segmental TTR
        """
        sample_no = 0
        msttr = 0
        for chunk in chunks(lemma_sequence, section_size):
            if len(chunk) == section_size:
                sample_no += 1
                msttr += safe_div(len(set(chunk)), section_size)
        return safe_div(msttr, sample_no)

    def determine_counts(self, lempos_tuples: Tuple[Tuple[str, str], ...]):
        filtered_lempos_tuples = tuple(
            filter(lambda lempos: not self.word_classifier.is_("misc", *lempos), lempos_tuples)
        )
        self.count_table["word"] = list(next(zip(*filtered_lempos_tuples)))

        for lemma, pos in filtered_lempos_tuples:
            is_sophisticated = False
            is_lexical = False
            is_verb = False

            if self.word_classifier.is_("noun", lemma, pos):
                self.count_table["noun"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a noun')

                self.count_table["lex"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif self.word_classifier.is_("adj", lemma, pos):
                self.count_table["adj"].append(lemma)
                logging.debug(f'Counted "{lemma}" as an adjective')

                self.count_table["lex"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif self.word_classifier.is_("adv", lemma, pos):
                self.count_table["adv"].append(lemma)
                logging.debug(f'Counted "{lemma}" as an adverb')

                self.count_table["lex"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif self.word_classifier.is_("verb", lemma, pos):
                self.count_table["verb"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a verb')

                self.count_table["lex"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True
                is_verb = True

            if self.word_classifier.is_("sword", lemma, pos):
                self.count_table["sword"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a sophisticated word')

                is_sophisticated = True

            if is_lexical and is_sophisticated:
                self.count_table["slex"].append(lemma)
                logging.debug(f'Counted "{lemma}" as a sophisticated lexical word')
                if is_verb:
                    self.count_table["sverb"].append(lemma)
                    logging.debug(f'Counted "{lemma}" as a sophisticated verb')

    def determine_freqs(self, *, section_size: Optional[int] = None) -> None:
        if section_size is None:
            section_size = self.section_size

        word_type_no = self.get_value("wordtypes")
        word_token_no = self.get_value("wordtokens")
        sword_type_no = self.get_value("swordtypes")
        lex_type_no = self.get_value("lextypes")
        lex_token_no = self.get_value("lextokens")
        slex_token_no = self.get_value("slextokens")
        verb_type_no = self.get_value("verbtypes")
        verb_token_no = self.get_value("verbtokens")
        sverb_type_no = self.get_value("sverbtypes")
        adj_type_no = self.get_value("adjtypes")
        adv_type_no = self.get_value("advtypes")
        noun_type_no = self.get_value("nountypes")
        noun_token_no = self.get_value("nountokens")

        # 1. Lexical density
        self.freq_table["LD"] = safe_div(lex_token_no, word_token_no)
        # 2. Lexical sophistication
        # 2.1 Lexical sophistication
        self.freq_table["LS1"] = safe_div(slex_token_no, lex_token_no)
        self.freq_table["LS2"] = safe_div(sword_type_no, word_type_no)

        # 2.2 Verb sophistication
        self.freq_table["VS1"] = safe_div(sverb_type_no, verb_token_no)
        self.freq_table["VS2"] = safe_div((sverb_type_no**2), verb_token_no)
        self.freq_table["CVS1"] = safe_div(sverb_type_no, _sqrt(2 * verb_token_no))

        # 3 Lexical diversity or variation
        # 3.1 NDW, may adjust the values of self.section_size
        self.freq_table["NDW"] = word_type_no
        self.freq_table["NDW-50"] = self.get_ndw_first_z(
            self.count_table["word"], section_size=self.section_size
        )
        self.freq_table["NDW-ER50"] = self.get_ndw_erz(
            self.count_table["word"], section_size=self.section_size, trials=self.ndw_trials
        )
        self.freq_table["NDW-ES50"] = self.get_ndw_esz(
            self.count_table["word"], section_size=self.section_size, trials=self.ndw_trials
        )

        # 3.2 TTR
        self.freq_table["TTR"] = safe_div(word_type_no, word_token_no)
        self.freq_table["MSTTR"] = (
            self.get_msttr(self.count_table["word"], section_size=self.section_size)
            if word_token_no >= self.section_size
            else self.freq_table["TTR"]
        )
        self.freq_table["CTTR"] = safe_div(word_type_no, _sqrt(2 * word_token_no))
        self.freq_table["RTTR"] = safe_div(word_type_no, _sqrt(word_token_no))
        self.freq_table["LogTTR"] = safe_div(_log(word_type_no), _log(word_token_no))
        self.freq_table["Uber"] = safe_div(
            _log(word_token_no, 10) * _log(word_token_no, 10),
            _log(safe_div(word_token_no, word_type_no), 10),
        )

        # 3.3 Verb diversity
        self.freq_table["VV1"] = safe_div(verb_type_no, verb_token_no)
        self.freq_table["SVV1"] = safe_div(verb_type_no * verb_type_no, verb_token_no)
        self.freq_table["CVV1"] = safe_div(verb_type_no, _sqrt(2 * verb_token_no))

        # 3.4 Lexical diversity
        self.freq_table["LV"] = safe_div(lex_type_no, lex_token_no)
        self.freq_table["VV2"] = safe_div(verb_type_no, lex_token_no)
        self.freq_table["NV"] = safe_div(noun_type_no, noun_token_no)
        self.freq_table["AdjV"] = safe_div(adj_type_no, lex_token_no)
        self.freq_table["AdvV"] = safe_div(adv_type_no, lex_token_no)
        self.freq_table["ModV"] = safe_div((adv_type_no + adj_type_no), lex_token_no)

    def determine_all_values(self, lempos_tuples: Tuple[Tuple[str, str], ...]) -> None:
        self.determine_counts(lempos_tuples)
        self.determine_freqs()

    def get_value(self, key: str, /, precision: int = 4) -> Union[int, float]:
        if (trimmed_key := key.removesuffix("types").removesuffix("tokens")) in self.COUNT_ITEMS:
            if key.endswith("types"):
                return len(set(self.count_table[trimmed_key]))
            elif key.endswith("tokens"):
                return len(self.count_table[trimmed_key])
            else:
                assert False, f"Unknown key: {key}"
        elif key in self.FREQ_ITEMS:
            assert (value := self.freq_table[key]) is not None
            return round(value, precision)
        else:
            raise ValueError(f"Unknown key: {key}")

    def get_matches(self, key: str, /) -> List[str]:
        if (trimmed_key := key.removesuffix("types").removesuffix("tokens")) in self.COUNT_ITEMS:
            if key.endswith("types"):
                return list(dict.fromkeys(self.count_table[trimmed_key]))
            elif key.endswith("tokens"):
                return self.count_table[trimmed_key]
            else:
                assert False, f"Unknown key: {key}"
        elif key in self.FREQ_ITEMS:
            return []
        else:
            raise ValueError(f"Unknown key: {key}")

    def get_all_values(self, precision: int = 4) -> dict:
        # TODO should store Filename in an extra metadata layer
        ret = OrderedDict({"Filepath": self.file_path})
        for sname in self.DEFAULT_MEASURES:
            ret[sname] = str(self.get_value(sname, precision))
        return ret

    def dump_matches(self, odir_matched: str = "", is_stdout: bool = False) -> None:  # pragma: no cover
        bn_input = os_path.basename(self.file_path)
        bn_input_noext = os_path.splitext(bn_input)[0]
        subodir_matched = os_path.join(odir_matched, bn_input_noext).strip()
        if not is_stdout:
            shutil.rmtree(subodir_matched, ignore_errors=True)
            os.makedirs(subodir_matched)
        for item in self.DEFAULT_MEASURES:
            if not (matches := self.get_matches(item)):
                continue

            res = "\n".join(matches)
            matches_id = f"{bn_input_noext}-{item}"
            if not is_stdout:
                extension = ".txt"
                fn_match_output = os_path.join(subodir_matched, matches_id + extension)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(f"{res}\n")
            else:
                sys.stdout.write(f"{matches_id}\n\n{res}\n")

    def __add__(self, other: "Ns_LCA_Counter") -> "Ns_LCA_Counter":
        logging.debug("Combining counters...")
        new_file_path = self.file_path + "+" + other.file_path if self.file_path else other.file_path
        new = Ns_LCA_Counter(new_file_path)
        for item in new.COUNT_ITEMS:
            new.count_table[item] = self.count_table[item] + other.count_table[item]
        new.determine_freqs()

        return new
