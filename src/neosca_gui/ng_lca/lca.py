#!/usr/bin/env python3

import logging
import os.path as os_path
import random
import string
import sys
from itertools import islice
from math import log, sqrt
from typing import Callable, Dict, List, Literal, Optional, Union

from neosca_gui import DATA_DIR
from neosca_gui.ng_io import SCAIO
from neosca_gui.ng_util import SCAProcedureResult


class LCA:
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
        is_cache_for_future_runs: bool = True,
        is_use_past_cache: bool = True,
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
        self.is_cache_for_future_runs = is_cache_for_future_runs
        self.is_use_past_cache = is_use_past_cache
        self.cache_extension = ".pickle.lzma"

        self.scaio = SCAIO()
        self.nlp_spacy: Optional[Callable] = None

        data_path = DATA_DIR / self.WORDLIST_DATAFILE_MAP[wordlist]
        logging.debug(f"Loading {data_path}...")
        data = self.scaio.load_pickle_lzma_file(data_path)
        self.word_dict = data["word_dict"]
        self.adj_dict = data["adj_dict"]
        self.verb_dict = data["verb_dict"]
        self.noun_dict = data["noun_dict"]
        self.word_ranks = sorted(self.word_dict.keys(), key=lambda w: self.word_dict[w], reverse=True)
        self.easy_words = self.word_ranks[:easy_word_threshold]

        self.TAGSET_CONDITION_MAP = {
            "ud": {
                "is_misc": self._is_misc_ud,
                "is_sword": self._is_sword_ud,
                "is_noun": self._is_noun_ud,
                "is_adj": self._is_adj_ud,
                "is_adv": self._is_adv_ud,
                "is_verb": self._is_verb_ud,
            },
            "ptb": {
                "is_misc": self._is_misc_ptb,
                "is_sword": self._is_sword_ptb,
                "is_noun": self._is_noun_ptb,
                "is_adj": self._is_adj_ptb,
                "is_adv": self._is_adv_ptb,
                "is_verb": self._is_verb_ptb,
            },
        }
        self.condition_map = self.TAGSET_CONDITION_MAP[tagset]

    def update_options(self, kwargs: Dict):
        self.__init__(**kwargs)

    def _is_misc_ud(self, lemma: str, pos: str) -> bool:
        if pos in ("PUNCT", "SYM", "X", "SPACE"):
            return True
        return False

    def _is_misc_ptb(self, lemma: str, pos: str) -> bool:
        if not lemma.strip():
            return True
        if pos[0] in string.punctuation:
            return True
        if pos in ("SENT", "SYM", "HYPH"):
            return True
        return False

    def _is_sword_ud(self, lemma: str, pos: str) -> bool:
        # sophisticated word
        if lemma not in self.easy_words and pos != "NUM":
            return True
        return False

    def _is_sword_ptb(self, lemma: str, pos: str) -> bool:
        if lemma not in self.easy_words and pos != "CD":
            return True
        return False

    def _is_noun_ud(self, lemma: str, pos: str) -> bool:
        # |UD    |PTB     |
        # |------|--------|
        # |NOUN  |NN, NNS |
        # |PROPN |NNP,NNPS|
        if pos in ("NOUN", "PROPN"):
            return True
        return False

    def _is_noun_ptb(self, lemma: str, pos: str) -> bool:
        if pos.startswith("N"):
            return True
        return False

    def _is_adj_ud(self, lemma: str, pos: str) -> bool:
        if pos == "ADJ":
            return True
        return False

    def _is_adj_ptb(self, lemma: str, pos: str) -> bool:
        if pos.startswith("J"):
            return True
        return False

    def _is_adv_ud(self, lemma: str, pos: str) -> bool:
        if pos != "ADV":
            return False
        if lemma in self.adj_dict:
            return True
        if lemma.endswith("ly") and lemma[:-2] in self.adj_dict:
            return True
        return False

    def _is_adv_ptb(self, lemma: str, pos: str) -> bool:
        if not pos.startswith("R"):
            return False
        if lemma in self.adj_dict:
            return True
        if lemma.endswith("ly") and lemma[:-2] in self.adj_dict:
            return True
        return False

    def _is_verb_ud(self, lemma: str, pos: str) -> bool:
        # Don't have to filter auxiliary verbs, because the VERB tag covers
        # main verbs (content verbs) but it does not cover auxiliary verbs and
        # verbal copulas (in the narrow sense), for which there is the AUX tag.
        #  https://universaldependencies.org/u/pos/VERB.html
        if pos == "VERB":
            return True
        return False

    def _is_verb_ptb(self, lemma: str, pos: str) -> bool:
        if not pos.startswith("V"):
            return False
        if lemma in ("be", "have"):
            return False
        return True

    def get_ndw_first_z(self, section_size, lemma_lst):
        """NDW for first 'section_size' words in a sample"""
        return len(set(lemma_lst[:section_size]))

    def get_ndw_erz(self, section_size, lemma_lst):
        """NDW expected random 'section_size' words, 10 trials"""
        ndw_erz = 0
        for _ in range(10):
            erz_lemma_lst = random.sample(lemma_lst, section_size)

            ndw_erz_types = set(erz_lemma_lst)
            ndw_erz += len(ndw_erz_types)
        return ndw_erz / 10

    def get_ndw_esz(self, section_size, lemma_lst):
        """NDW expected random sequences of 'section_size' words, 10 trials"""
        ndw_esz = 0
        for _ in range(10):
            start_word = random.randint(0, len(lemma_lst) - section_size)
            esz_lemma_lst = lemma_lst[start_word : start_word + section_size]

            ndw_esz_types = set(esz_lemma_lst)
            ndw_esz += len(ndw_esz_types)
        return ndw_esz / 10

    # https://stackoverflow.com/a/22045226/20732031
    def _chunk(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    def get_msttr(self, section_size: int, lemma_lst: List[str]):
        """
        Mean Segmental TTR
        """
        sample_nr = 0
        msttr = 0
        for chunk in self._chunk(lemma_lst, section_size):
            if len(chunk) == section_size:
                sample_nr += 1
                msttr += len(set(chunk)) / section_size if section_size else 0
        return msttr / sample_nr if sample_nr else 0

    def _safe_div(self, n1: Union[int, float], n2: Union[int, float]) -> float:
        return n1 / n2 if n2 else 0

    def compute(
        self,
        word_count_map,
        sword_count_map,
        lex_count_map,
        slex_count_map,
        verb_count_map,
        sverb_count_map,
        adj_count_map,
        adv_count_map,
        noun_count_map,
        lemma_lst,
    ):
        word_type_nr = len(word_count_map)
        word_token_nr = sum(word_count_map.values())
        lemma_nr = word_token_nr

        sword_type_nr = len(sword_count_map)
        sword_token_nr = sum(sword_count_map.values())

        lex_type_nr = len(lex_count_map)
        lex_token_nr = sum(lex_count_map.values())

        slex_type_nr = len(slex_count_map)
        slex_token_nr = sum(slex_count_map.values())

        verb_type_nr = len(verb_count_map)
        verb_token_nr = sum(verb_count_map.values())

        sverb_type_nr = len(sverb_count_map)
        # sverb_token_nr = sum(sverb_count_map.values())

        adj_type_nr = len(adj_count_map)
        # adj_token_nr = sum(adj_count_map.values())

        adv_type_nr = len(adv_count_map)
        # adv_token_nr = sum(adv_count_map.values())

        noun_type_nr = len(noun_count_map)
        noun_token_nr = sum(noun_count_map.values())

        # 1. Lexical density
        lexical_density = self._safe_div(lex_token_nr, word_token_nr)

        # 2. Lexical sophistication
        # 2.1 Lexical sophistication
        lexical_sophistication1 = self._safe_div(slex_token_nr, lex_token_nr)
        lexical_sophistication2 = self._safe_div(sword_type_nr, word_type_nr)

        # 2.2 Verb sophistication
        verb_sophistication1 = self._safe_div(sverb_type_nr, verb_token_nr)
        verb_sophistication2 = self._safe_div((sverb_type_nr**2), verb_token_nr)
        corrected_verb_sophistication1 = self._safe_div(sverb_type_nr, sqrt(2 * verb_token_nr))

        # 3 Lexical diversity or variation

        # 3.1 NDW, may adjust the values of "self.section_size"
        ndw = ndwz = ndwerz = ndwesz = word_type_nr
        if lemma_nr >= self.section_size:
            ndwz = self.get_ndw_first_z(self.section_size, lemma_lst)
            ndwerz = self.get_ndw_erz(self.section_size, lemma_lst)
            ndwesz = self.get_ndw_esz(self.section_size, lemma_lst)

        # 3.2 TTR
        msttr = ttr = self._safe_div(word_type_nr, word_token_nr)
        if lemma_nr >= self.section_size:
            msttr = self.get_msttr(self.section_size, lemma_lst)
        cttr = self._safe_div(word_type_nr, sqrt(2 * word_token_nr))
        rttr = self._safe_div(word_type_nr, sqrt(word_token_nr))
        logttr = self._safe_div(log(word_type_nr), log(word_token_nr))
        uber = self._safe_div(
            log(word_token_nr, 10) * log(word_token_nr, 10),
            log(self._safe_div(word_token_nr, word_type_nr), 10),
        )

        # 3.3 Verb diversity
        verb_variation1 = self._safe_div(verb_type_nr, verb_token_nr)
        squared_verb_variation1 = self._safe_div(verb_type_nr * verb_type_nr, verb_token_nr)
        corrected_verb_variation1 = self._safe_div(verb_type_nr, sqrt(2 * verb_token_nr))

        # 3.4 Lexical diversity
        lexical_word_variation = self._safe_div(lex_type_nr, lex_token_nr)
        verb_variation2 = self._safe_div(verb_type_nr, lex_token_nr)
        noun_variation = self._safe_div(noun_type_nr, noun_token_nr)
        adjective_variation = self._safe_div(adj_type_nr, lex_token_nr)
        adverb_variation = self._safe_div(adv_type_nr, lex_token_nr)
        modifier_variation = self._safe_div((adv_type_nr + adj_type_nr), lex_token_nr)

        return (
            word_type_nr,
            sword_type_nr,
            lex_type_nr,
            slex_type_nr,
            word_token_nr,
            sword_token_nr,
            lex_token_nr,
            slex_token_nr,
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
        )

    def _analyze(self, *, file_path: Optional[str] = None, doc=None):
        from neosca_gui.ng_nlp import Ng_NLP_Stanza

        assert (not file_path) ^ (not doc)

        if file_path is not None:
            logging.info(f"Processing {file_path}...")
            cache_path = os_path.splitext(file_path)[0] + self.cache_extension
            if self.is_use_past_cache and SCAIO.has_valid_cache(file_path=file_path, cache_path=cache_path):
                logging.info(
                    f"Loading cache: {cache_path} already exists, and is non-empty and newer than {file_path}."
                )
                doc = Ng_NLP_Stanza.serialized2doc(SCAIO.load_lzma_file(cache_path))
            else:
                doc = self.scaio.read_file(file_path)
        else:
            file_path = "cmdline_text"
            cache_path = file_path + self.cache_extension

        if doc is None:
            return None
        lemma_pos_gen = Ng_NLP_Stanza.get_lemma_and_pos(
            doc,
            tagset=self.tagset,
            is_cache_for_future_runs=self.is_cache_for_future_runs,
            cache_path=cache_path,
        )

        word_count_map: Dict[str, int] = {}
        sword_count_map: Dict[str, int] = {}
        lex_count_map: Dict[str, int] = {}
        slex_count_map: Dict[str, int] = {}
        verb_count_map: Dict[str, int] = {}
        sverb_count_map: Dict[str, int] = {}
        adj_count_map: Dict[str, int] = {}
        adv_count_map: Dict[str, int] = {}
        noun_count_map: Dict[str, int] = {}
        lemma_lst = []
        condition_map = self.condition_map
        # Universal POS tags: https://universaldependencies.org/u/pos/
        for lemma, pos in lemma_pos_gen:
            if condition_map["is_misc"](lemma, pos):
                continue

            is_sophisticated = False
            is_lexical = False
            is_verb = False

            word_count_map[lemma] = word_count_map.get(lemma, 0) + 1
            lemma_lst.append(lemma)

            if condition_map["is_noun"](lemma, pos):
                noun_count_map[lemma] = noun_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a noun')

                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif condition_map["is_adj"](lemma, pos):
                adj_count_map[lemma] = adj_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as an adjective')

                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif condition_map["is_adv"](lemma, pos):
                adv_count_map[lemma] = adv_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as an adverb')

                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True

            elif condition_map["is_verb"](lemma, pos):
                verb_count_map[lemma] = verb_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a verb')

                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                is_lexical = True
                is_verb = True

            if condition_map["is_sword"](lemma, pos):
                sword_count_map[lemma] = sword_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a sophisticated word')

                is_sophisticated = True

            if is_lexical and is_sophisticated:
                slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a sophisticated lexical word')
                if is_verb:
                    sverb_count_map[lemma] = sverb_count_map.get(lemma, 0) + 1
                    logging.debug(f'Counted "{lemma}" as a sophisticated verb')

        values = self.compute(
            word_count_map,
            sword_count_map,
            lex_count_map,
            slex_count_map,
            verb_count_map,
            sverb_count_map,
            adj_count_map,
            adv_count_map,
            noun_count_map,
            lemma_lst,
        )
        if values is None:
            return values
        values = [str(round(v, self.precision)) for v in values]
        values.insert(0, file_path)
        return values

    def analyze(self, *, ifiles: Optional[List[str]] = None, text: Optional[str] = None) -> SCAProcedureResult:
        if not (ifiles is None) ^ (text is None):
            return False, "One and only one of (input files, text) should be given."

        import csv

        handle = sys.stdout if self.is_stdout else open(self.ofile, "w", encoding="utf-8", newline="")  # noqa: SIM115

        csv_writer = csv.writer(handle)
        csv_writer.writerow(self.FIELDNAMES)

        if text is not None:
            values = self._analyze(doc=text)
            if values is not None:
                csv_writer.writerow(values)

        else:
            for ifile in ifiles:  # type: ignore
                values = self._analyze(file_path=ifile)
                if values is not None:
                    csv_writer.writerow(values)

        handle.close()

        return True, None

    def ensure_spacy_initialized(func: Callable):  # type:ignore
        def wrapper(self, *args, **kwargs):
            if self.nlp_spacy is None:
                logging.info("Initializing spaCy...")
                import spacy  # type: ignore

                # default spacy pipeline: "tok2vec", "tagger", "parser",
                #  "attribute_ruler", "lemmatizer", "ner"
                self.nlp_spacy = spacy.load("en_core_web_sm", exclude=["ner", "parser"])

            return func(self, *args, **kwargs)

        return wrapper
