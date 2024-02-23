#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import random
import sys
from math import log, sqrt
from typing import Dict, List, Literal, Optional, Sequence, Tuple, Union

from neosca import DATA_DIR
from neosca.ns_io import Ns_Cache, Ns_IO
from neosca.ns_lca import word_classifiers
from neosca.ns_utils import Ns_Procedure_Result, chunks, safe_div


class Ns_LCA:
    FIELDNAMES = (
        "Filepath",
        "wordtypes",
        "swordtypes",
        "lextypes",
        "slextypes",
        "wordtokens",
        "swordtokens",
        "lextokens",
        "slextokens",
        "LD",
        "LS1",
        "LS2",
        "VS1",
        "VS2",
        "CVS1",
        "NDW",
        "NDW-50",
        "NDW-ER50",
        "NDW-ES50",
        "TTR",
        "MSTTR",
        "CTTR",
        "RTTR",
        "LogTTR",
        "Uber",
        "LV",
        "VV1",
        "SVV1",
        "CVV1",
        "VV2",
        "NV",
        "AdjV",
        "AdvV",
        "ModV",
    )

    WORDLIST_DATAFILE_MAP = {
        "bnc": "bnc_all_filtered.pickle.lzma",
        "anc": "anc_all_count.pickle.lzma",
    }

    def __init__(
        self,
        wordlist: str = "bnc",
        tagset: Literal["ud", "ptb"] = "ud",
        easy_word_threshold: int = 2000,
        section_size: int = 50,
        precision: int = 4,
        ofile: str = "result.csv",
        is_stdout: bool = False,
        is_cache: bool = True,
        is_use_cache: bool = True,
    ) -> None:
        assert wordlist in ("bnc", "anc")
        assert tagset in ("ud", "ptb")
        logging.debug(f"Using {wordlist.upper()} wordlist")
        self.wordlist = wordlist
        logging.debug(f"Using {tagset.upper()} POS tagset")
        assert tagset in ("ud", "ptb")
        self.tagset: Literal["ud", "ptb"] = tagset

        self.section_size = section_size
        self.precision = precision
        self.ofile = ofile
        self.is_stdout = is_stdout
        self.is_cache = is_cache
        self.is_use_cache = is_use_cache

        word_data_path = DATA_DIR / self.WORDLIST_DATAFILE_MAP[wordlist]
        logging.debug(f"Loading {word_data_path}...")
        word_data = Ns_IO.load_pickle_lzma(word_data_path)
        self.word_classifier = {
            "ud": word_classifiers.UD_Word_Classifier,
            "ptb": word_classifiers.PTB_Word_Classifier,
        }[self.tagset](word_data, easy_word_threshold)

    def get_ndw_first_z(self, lemmas: Sequence[str], section_size: int):
        """NDW for first 'section_size' words in a sample"""
        if len(lemmas) < section_size:
            return len(set(lemmas))
        return len(set(lemmas[:section_size]))

    def get_ndw_erz(self, lemmas: Sequence[str], section_size: int, trials: int = 10):
        """NDW expected random 'section_size' words, 10 trials by default"""
        if len(lemmas) < section_size:
            return len(set(lemmas))
        ndw_erz = 0
        for _ in range(trials):
            erz_lemma_lst = random.sample(lemmas, section_size)

            ndw_erz_types = set(erz_lemma_lst)
            ndw_erz += len(ndw_erz_types)
        return ndw_erz / 10

    def get_ndw_esz(self, lemmas: Sequence[str], section_size: int, trials: int = 10):
        """NDW expected random sequences of 'section_size' words, 10 trials by default"""
        if len(lemmas) < section_size:
            return len(set(lemmas))
        ndw_esz = 0
        for _ in range(trials):
            start_word = random.randint(0, len(lemmas) - section_size)
            esz_lemma_lst = lemmas[start_word : start_word + section_size]

            ndw_esz_types = set(esz_lemma_lst)
            ndw_esz += len(ndw_esz_types)
        return ndw_esz / 10

    def get_msttr(self, lemmas: Sequence[str], section_size: int):
        """
        Mean Segmental TTR
        """
        sample_no = 0
        msttr = 0
        for chunk in chunks(lemmas, section_size):
            if len(chunk) == section_size:
                sample_no += 1
                msttr += safe_div(len(set(chunk)), section_size)
        return safe_div(msttr, sample_no)

    def get_lempos_frm_text(self, text: str, cache_path: Optional[str] = None) -> Tuple[Tuple[str, str], ...]:
        from neosca.ns_nlp import Ns_NLP_Stanza

        return Ns_NLP_Stanza.get_lemma_and_pos(text, tagset=self.tagset, cache_path=cache_path)

    def get_lempos_frm_file(self, file_path: str) -> Tuple[Tuple[str, str], ...]:
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
            return Ns_NLP_Stanza.get_lemma_and_pos(text, tagset=self.tagset, cache_path=cache_path)
        except BaseException as e:
            # If cache is generated at current run, remove it as it is potentially broken
            if cache_path is not None and os_path.exists(cache_path) and not is_cache_available:
                os.remove(cache_path)
            raise e

    def get_basic_profile_frm_lempos(
        self, lempos_tuples: Tuple[Tuple[str, str], ...]
    ) -> Tuple[Tuple[str, ...], Dict[str, Dict[str, int]]]:
        profile_table: Dict[str, Dict[str, int]] = {
            "sword": {},
            "lex": {},
            "slex": {},
            "verb": {},
            "sverb": {},
            "adj": {},
            "adv": {},
            "noun": {},
        }

        filtered_lempos_tuples = tuple(
            filter(lambda lempos: not self.word_classifier.is_("misc", *lempos), lempos_tuples)
        )
        for lemma, pos in filtered_lempos_tuples:
            is_sophisticated = False
            is_lexical = False
            is_verb = False

            if self.word_classifier.is_("noun", lemma, pos):
                profile_table["noun"][lemma] = profile_table["noun"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a noun')

                profile_table["lex"][lemma] = profile_table["lex"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif self.word_classifier.is_("adj", lemma, pos):
                profile_table["adj"][lemma] = profile_table["adj"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as an adjective')

                profile_table["lex"][lemma] = profile_table["lex"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif self.word_classifier.is_("adv", lemma, pos):
                profile_table["adv"][lemma] = profile_table["adv"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as an adverb')

                profile_table["lex"][lemma] = profile_table["lex"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif self.word_classifier.is_("verb", lemma, pos):
                profile_table["verb"][lemma] = profile_table["verb"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a verb')

                profile_table["lex"][lemma] = profile_table["lex"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True
                is_verb = True

            if self.word_classifier.is_("sword", lemma, pos):
                profile_table["sword"][lemma] = profile_table["sword"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a sophisticated word')

                is_sophisticated = True

            if is_lexical and is_sophisticated:
                profile_table["slex"][lemma] = profile_table["slex"].get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a sophisticated lexical word')
                if is_verb:
                    profile_table["sverb"][lemma] = profile_table["sverb"].get(lemma, 0) + 1
                    logging.debug(f'Counted "{lemma}" as a sophisticated verb')

        lemmas = tuple(lempos[0] for lempos in lempos_tuples)
        return lemmas, profile_table

    def get_values_frm_profile(
        self, lemmas: Sequence[str], profile_table: Dict[str, Dict[str, int]]
    ) -> List[Union[int, float]]:
        word_type_no = len(set(lemmas))
        word_token_no = len(lemmas)
        sword_type_no = len(profile_table["sword"])
        sword_token_no = sum(profile_table["sword"].values())
        lex_type_no = len(profile_table["lex"])
        lex_token_no = sum(profile_table["lex"].values())
        slex_type_no = len(profile_table["slex"])
        slex_token_no = sum(profile_table["slex"].values())
        verb_type_no = len(profile_table["verb"])
        verb_token_no = sum(profile_table["verb"].values())
        sverb_type_no = len(profile_table["sverb"])
        # sverb_token_no = sum(profile_table["sverb"].values())
        adj_type_no = len(profile_table["adj"])
        # adj_token_no = sum(profile_table["adj"].values())
        adv_type_no = len(profile_table["adv"])
        # adv_token_no = sum(profile_table["adv"].values())
        noun_type_no = len(profile_table["noun"])
        noun_token_no = sum(profile_table["noun"].values())

        # 1. Lexical density
        lexical_density = safe_div(lex_token_no, word_token_no)
        # 2. Lexical sophistication
        # 2.1 Lexical sophistication
        lexical_sophistication1 = safe_div(slex_token_no, lex_token_no)
        lexical_sophistication2 = safe_div(sword_type_no, word_type_no)

        # 2.2 Verb sophistication
        verb_sophistication1 = safe_div(sverb_type_no, verb_token_no)
        verb_sophistication2 = safe_div((sverb_type_no**2), verb_token_no)
        corrected_verb_sophistication1 = safe_div(sverb_type_no, sqrt(2 * verb_token_no))

        # 3 Lexical diversity or variation
        # 3.1 NDW, may adjust the values of self.section_size
        ndw = word_type_no
        ndwz = self.get_ndw_first_z(lemmas, self.section_size)
        ndwerz = self.get_ndw_erz(lemmas, self.section_size)
        ndwesz = self.get_ndw_esz(lemmas, self.section_size)

        # 3.2 TTR
        ttr = safe_div(word_type_no, word_token_no)
        msttr = self.get_msttr(lemmas, self.section_size) if word_token_no >= self.section_size else ttr
        cttr = safe_div(word_type_no, sqrt(2 * word_token_no))
        rttr = safe_div(word_type_no, sqrt(word_token_no))
        logttr = safe_div(log(word_type_no), log(word_token_no))
        uber = safe_div(
            log(word_token_no, 10) * log(word_token_no, 10),
            log(safe_div(word_token_no, word_type_no), 10),
        )

        # 3.3 Verb diversity
        verb_variation1 = safe_div(verb_type_no, verb_token_no)
        squared_verb_variation1 = safe_div(verb_type_no * verb_type_no, verb_token_no)
        corrected_verb_variation1 = safe_div(verb_type_no, sqrt(2 * verb_token_no))

        # 3.4 Lexical diversity
        lexical_word_variation = safe_div(lex_type_no, lex_token_no)
        verb_variation2 = safe_div(verb_type_no, lex_token_no)
        noun_variation = safe_div(noun_type_no, noun_token_no)
        adjective_variation = safe_div(adj_type_no, lex_token_no)
        adverb_variation = safe_div(adv_type_no, lex_token_no)
        modifier_variation = safe_div((adv_type_no + adj_type_no), lex_token_no)

        return list(
            map(
                lambda n: round(n, self.precision),
                (
                    word_type_no,
                    sword_type_no,
                    lex_type_no,
                    slex_type_no,
                    word_token_no,
                    sword_token_no,
                    lex_token_no,
                    slex_token_no,
                    lexical_density,
                    lexical_sophistication1,
                    lexical_sophistication2,
                    verb_sophistication1,
                    verb_sophistication2,
                    corrected_verb_sophistication1,
                    ndw,
                    ndwz,
                    ndwerz,
                    ndwesz,
                    ttr,
                    msttr,
                    cttr,
                    rttr,
                    logttr,
                    uber,
                    lexical_word_variation,
                    verb_variation1,
                    squared_verb_variation1,
                    corrected_verb_variation1,
                    verb_variation2,
                    noun_variation,
                    adjective_variation,
                    adverb_variation,
                    modifier_variation,
                ),
            )
        )

    def _analyze(self, *, file_path: Optional[str] = None, doc=None) -> List[Union[int, float]]:
        if file_path is not None:
            lempos_tuples = self.get_lempos_frm_file(file_path)
        elif doc is not None:
            lempos_tuples = self.get_lempos_frm_text(doc)
        else:
            assert False, "file_path and doc are mutually exclusive"

        lemmas, profile_table = self.get_basic_profile_frm_lempos(lempos_tuples)
        return self.get_values_frm_profile(lemmas, profile_table)

    def analyze(self, *, ifiles: Optional[List[str]] = None, text: Optional[str] = None) -> Ns_Procedure_Result:
        if not (ifiles is None) ^ (text is None):
            return False, "One and only one of (input files, text) should be given."

        import csv

        handle = sys.stdout if self.is_stdout else open(self.ofile, "w", encoding="utf-8", newline="")  # noqa: SIM115

        csv_writer = csv.writer(handle)
        csv_writer.writerow(self.FIELDNAMES)

        if text is not None:
            values = self._analyze(doc=text)
            if values is not None:
                csv_writer.writerow(("cli_text", *values))

        else:
            for ifile in ifiles:  # type: ignore
                values = self._analyze(file_path=ifile)
                if values is not None:
                    csv_writer.writerow((ifile, *values))

        handle.close()

        return True, None
