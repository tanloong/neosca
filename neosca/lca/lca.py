#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import logging
from math import log, sqrt
import os.path as os_path
import random
import sys
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

from ..scaio import SCAIO
from ..util import SCAProcedureResult


class LCA:
    def __init__(
        self, wordlist: str, ofile: str = "result.csv", is_stdout: bool = False
    ) -> None:
        self.ofile = ofile
        self.is_stdout = is_stdout

        self.scaio = SCAIO()
        self.nlp_spacy: Optional[Callable] = None

        assert wordlist in ("bnc", "anc")
        wordlist_datafile_map = {
            "bnc": "bnc_all_filtered.pickle.lzma",
            "anc": "anc_all_count.pickle.lzma",
        }
        data_dir = os_path.join(os_path.dirname(os_path.dirname(__file__)), "data")
        datafile = os_path.join(data_dir, wordlist_datafile_map[wordlist])
        logging.debug(f"Loading {datafile}...")
        data = self.scaio.load_pickle_lzma_file(datafile)

        word_dict = data["word_dict"]
        adj_dict = data["adj_dict"]
        verb_dict = data["verb_dict"]
        noun_dict = data["noun_dict"]
        word_ranks = self._sort_by_value(word_dict)
        easy_words = word_ranks[-2000:]

        self.word_dict = word_dict
        self.adj_dict = adj_dict
        self.verb_dict = verb_dict
        self.noun_dict = noun_dict
        self.word_ranks = word_ranks
        self.easy_words = easy_words

        # adjust minimum sample size here
        self.standard = 50

    def _sort_by_value(self, d):
        """Returns the keys of dictionary d sorted by their values"""
        items = d.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort()
        return [backitems[i][1] for i in range(0, len(backitems))]

    def get_ndw_first_z(self, z, lemma_lst):
        """NDW for first z words in a sample"""
        ndw_first_z_types = {}
        for lemma in lemma_lst[:z]:
            ndw_first_z_types[lemma] = 1
        return len(ndw_first_z_types)

    def get_ndw_erz(self, z, lemma_lst):
        """NDW expected random z words, 10 trials"""
        ndw_erz = 0
        for _ in range(10):
            erz_lemma_lst = random.sample(lemma_lst, z)

            ndw_erz_types = set(erz_lemma_lst)
            ndw_erz += len(ndw_erz_types)
        return ndw_erz / 10

    def get_ndw_esz(self, z, lemma_lst):
        """NDW expected random sequences of z words, 10 trials"""
        ndw_esz = 0
        for _ in range(10):
            start_word = random.randint(0, len(lemma_lst) - z)
            esz_lemma_lst = lemma_lst[start_word : start_word + z]

            ndw_esz_types = set(esz_lemma_lst)
            ndw_esz += len(ndw_esz_types)
        return ndw_esz / 10

    def get_msttr(self, z, lemma_lst):
        sample_nr = 0
        msttr = 0
        while len(lemma_lst) >= z:
            sample_nr += 1
            msttr_types = {}
            for lemma in lemma_lst[:z]:
                msttr_types[lemma] = 1
            msttr += len(msttr_types) / z if z else 0
            lemma_lst = lemma_lst[z:]
        return msttr / sample_nr if sample_nr else 0

    def _analyze(
        self,
        *,
        filepath: Optional[str] = None,
        text: Optional[str] = None,
    ):
        assert (not filepath) ^ (not text)

        if filepath is not None:
            logging.info(f"Processing {filepath}...")
            text = self.scaio.read_file(filepath)

        if text is None:
            return None

        easy_words = self.easy_words
        adj_dict = self.adj_dict
        # verb_dict = self.verb_dict
        # noun_dict = self.noun_dict

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

        g = self.get_lemma_pos_tuple(text)

        # Universal POS tags: https://universaldependencies.org/u/pos/
        for lemma, pos in g:
            if pos in ("PUNCT", "SYM", "X", "SPACE"):
                continue

            word_count_map[lemma] = word_count_map.get(lemma, 0) + 1
            lemma_lst.append(lemma)

            if (lemma not in easy_words) and pos != "NUM":
                sword_count_map[lemma] = sword_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a sophisticated word')

            # |UD    |PTB     |
            # |------|--------|
            # |NOUN  |NN, NNS |
            # |PROPN |NNP,NNPS|
            if pos in ("NOUN", "PROPN"):
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                noun_count_map[lemma] = noun_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a noun')

                if lemma not in easy_words:
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
                    logging.debug(f'Counted "{lemma}" as a sophisticated lexical word')
            elif pos == "ADJ":
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                adj_count_map[lemma] = adj_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as an adjective')

                if lemma not in easy_words:
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
                    logging.debug(f'Counted "{lemma}" as a sophisticated lexical word')
            elif pos == "ADV" and (
                (lemma in adj_dict) or (lemma.endswith("ly") and lemma[:-2] in adj_dict)
            ):
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                adv_count_map[lemma] = adv_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as an adverb')

                if lemma not in easy_words:
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
                    logging.debug(f'Counted "{lemma}" as a sophisticated lexical word')
            # Don't have to filter auxiliary verbs, because the VERB tag covers
            #  main verbs (content verbs) but it does not cover auxiliary verbs
            #  and verbal copulas (in the narrow sense), for which there is the
            #  AUX tag.
            #  https://universaldependencies.org/u/pos/VERB.html
            elif pos == "VERB":
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a lexical word')

                verb_count_map[lemma] = verb_count_map.get(lemma, 0) + 1
                logging.debug(f'Counted "{lemma}" as a verb')

                if lemma not in easy_words:
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
                    logging.debug(f'Counted "{lemma}" as a sophisticated lexical word')

                    sverb_count_map[lemma] = sverb_count_map.get(lemma, 0) + 1
                    logging.debug(f'Counted "{lemma}" as a sophisticated verb')
        return self.compute(
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

    def div(self, n1: Union[int, float], n2: Union[int, float]) -> float:
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
        word_token_nr = sum(count for count in word_count_map.values())
        lemma_nr = word_token_nr

        sword_type_nr = len(sword_count_map)
        sword_token_nr = sum(count for count in sword_count_map.values())

        lex_type_nr = len(lex_count_map)
        lex_token_nr = sum(count for count in lex_count_map.values())

        slex_type_nr = len(slex_count_map)
        slex_token_nr = sum(count for count in slex_count_map.values())

        verb_type_nr = len(verb_count_map)
        verb_token_nr = sum(count for count in verb_count_map.values())

        sverb_type_nr = len(sverb_count_map)
        # sverb_token_nr = sum(count for count in sverb_count_map.values())

        adj_type_nr = len(adj_count_map)
        # adj_token_nr = sum(count for count in adj_count_map.values())

        adv_type_nr = len(adv_count_map)
        # adv_token_nr = sum(count for count in adv_count_map.values())

        noun_type_nr = len(noun_count_map)
        noun_token_nr = sum(count for count in noun_count_map.values())

        # 1. lexical density
        ld = self.div(lex_token_nr, word_token_nr)

        # 2. lexical sophistication
        # 2.1 lexical sophistication
        ls1 = self.div(slex_token_nr, lex_token_nr)
        ls2 = self.div(sword_type_nr, word_type_nr)

        # 2.2 verb sophistication
        vs1 = self.div(sverb_type_nr, verb_token_nr)
        vs2 = self.div((sverb_type_nr**2), verb_token_nr)
        cvs1 = self.div(sverb_type_nr, sqrt(2 * verb_token_nr))

        # 3 lexical diversity or variation

        # 3.1 NDW, may adjust the values of "self.standard"
        ndw = ndwz = ndwerz = ndwesz = word_type_nr
        if lemma_nr >= self.standard:
            ndwz = self.get_ndw_first_z(self.standard, lemma_lst)
            ndwerz = self.get_ndw_erz(self.standard, lemma_lst)
            ndwesz = self.get_ndw_esz(self.standard, lemma_lst)

        # 3.2 TTR
        msttr = ttr = self.div(word_type_nr, word_token_nr)
        if lemma_nr >= self.standard:
            msttr = self.get_msttr(self.standard, lemma_lst)
        cttr = self.div(word_type_nr, sqrt(2 * word_token_nr))
        rttr = self.div(word_type_nr, sqrt(word_token_nr))
        logttr = self.div(log(word_type_nr), log(word_token_nr))
        uber = self.div(
            log(word_token_nr, 10) * log(word_token_nr, 10),
            log(self.div(word_token_nr, word_type_nr), 10),
        )

        # 3.3 verb diversity
        vv1 = self.div(verb_type_nr, verb_token_nr)
        svv1 = self.div(verb_type_nr * verb_type_nr, verb_token_nr)
        cvv1 = self.div(verb_type_nr, sqrt(2 * verb_token_nr))

        # 3.4 lexical diversity
        lv = self.div(lex_type_nr, lex_token_nr)
        vv2 = self.div(verb_type_nr, lex_token_nr)
        nv = self.div(noun_type_nr, noun_token_nr)
        adjv = self.div(adj_type_nr, lex_token_nr)
        advv = self.div(adv_type_nr, lex_token_nr)
        modv = self.div((adv_type_nr + adj_type_nr), lex_token_nr)

        return (
            word_type_nr,
            sword_type_nr,
            lex_type_nr,
            slex_type_nr,
            word_token_nr,
            sword_token_nr,
            lex_token_nr,
            slex_token_nr,
            ld,
            ls1,
            ls2,
            vs1,
            vs2,
            cvs1,
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
            lv,
            vv1,
            svv1,
            cvv1,
            vv2,
            nv,
            adjv,
            advv,
            modv,
        )

    def analyze(
        self, *, ifiles: Optional[List[str]] = None, text: Optional[str] = None
    ) -> SCAProcedureResult:
        if not (ifiles is None) ^ (text is None):
            return False, "One and only one of (input files, text) should be given."

        import csv

        handle = (
            open(self.ofile, "w", encoding="utf-8", newline="")
            if not self.is_stdout
            else sys.stdout
        )
        fieldnames = (
            "filename",
            "wordtypes (word types)",
            "swordtypes (sophisticated word types)",
            "lextypes (lexical types)",
            "slextypes (sophisticated lexical types)",
            "wordtokens (word tokens)",
            "swordtokens (sophisticated word tokens)",
            "lextokens (lexical tokens)",
            "slextokens (sophisticated lexical tokens)",
            "LD (lexical density)",
            "LS1 (lexical sophistication-I)",
            "LS2 (lexical sophistication-II)",
            "VS1 (verb sophistication-I)",
            "VS2 (verb sophistication-II)",
            "CVS1 (corrected VS1)",
            "NDW (number of different words)",
            "NDW-50 (NDW, first 50 words)",
            "NDW-ER50 (NDW, expected random 50)",
            "NDW-ES50 (NDW, expected sequence 50)",
            "TTR (type-token ratio)",
            "MSTTR (mean segmental TTR, 50)",
            "CTTR (corrected TTR)",
            "RTTR (root TTR)",
            "LogTTR (bilogarithmic TTR)",
            "Uber (Uber Index)",
            "LV (lexical word variation)",
            "VV1 (verb variation-I)",
            "SVV1 (squared VV1)",
            "CVV1 (corrected VV1)",
            "VV2 (verb variation-II)",
            "NV (noun variation)",
            "AdjV (adjective variation)",
            "AdvV (adverb variation)",
            "ModV (modifier variation)",
        )
        csv_writer = csv.writer(handle)
        csv_writer.writerow(fieldnames)

        if text is not None:
            values = self._analyze(text=text)
            if values is not None:
                values = [str(round(v, 4)) for v in values]
                values.insert(0, "cmdline_text")
                csv_writer.writerow(values)

        else:
            for ifile in ifiles:  # type: ignore
                values = self._analyze(filepath=ifile)
                if values is not None:
                    values = [str(round(v, 4)) for v in values]
                    values.insert(0, ifile)
                    csv_writer.writerow(values)

        handle.close()

        if not self.is_stdout:
            logging.info(f"Output has been saved to {self.ofile}. Done.")

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

    @ensure_spacy_initialized
    def get_lemma_pos_tuple(self, text: str) -> Generator[Tuple[str, str], Any, None]:
        doc = self.nlp_spacy(text)  # type:ignore
        for token in doc:
            yield (token.lemma_.lower(), token.pos_)