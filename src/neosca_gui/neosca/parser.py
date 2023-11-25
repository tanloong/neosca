#!/usr/bin/env python3

import logging
import lzma
from typing import Generator, Literal, Optional, Tuple, Union

from stanza import Document

from neosca_gui.ng_nlp import Ng_NLP_Stanza


class Ns_SCA_Parser:
    @classmethod
    def parse(
        cls,
        doc: Union[str, Document],
        is_cache: bool = False,
        cache_path: Optional[str] = None,
        processors: Optional[tuple] = None,
    ) -> Document:
        if cache_path is None:
            cache_path = "cmdline_text.pickle.lzma"

        has_just_processed: bool = False
        if processors is None:
            processors = Ng_NLP_Stanza.processors

        if isinstance(doc, str):
            logging.debug("Processing bare text...")
            doc = Ng_NLP_Stanza.nlp(doc, processors=processors)
            has_just_processed = True
        else:
            attr = "processors"
            existing_processors = set(getattr(doc, attr)) if hasattr(doc, attr) else set()
            filtered_processors = set(processors) - existing_processors
            if filtered_processors:
                logging.debug(
                    f"Processing partially parsed document with additional processors {filtered_processors}"
                )
                doc = Ng_NLP_Stanza.nlp(doc, processors=tuple(filtered_processors))
                setattr(doc, attr, existing_processors | filtered_processors)
                has_just_processed = True

        if has_just_processed and is_cache:
            logging.debug(f"Caching document to {cache_path}")
            with open(cache_path, "wb") as f:
                f.write(lzma.compress(Ng_NLP_Stanza.doc2serialized(doc)))
        return doc

    @classmethod
    def doc2tree(cls, doc: Document) -> str:
        return "\n".join(sent.constituency.pretty_print() for sent in doc.sentences)

    @classmethod
    def get_constituency_tree(
        cls, doc: Union[str, Document], is_cache: bool = False, cache_path: Optional[str] = None
    ) -> str:
        if cache_path is None:
            cache_path = "cmdline_text.pickle.lzma"
        doc = cls.parse(doc, is_cache, cache_path, processors=("tokenize", "pos", "constituency"))
        return cls.doc2tree(doc)

    @classmethod
    def get_lemma_and_pos(
        cls,
        doc: Union[str, Document],
        tagset: Literal["ud", "ptb"],
        is_cache: bool = False,
        cache_path: str = "cmdline_text.pkl.lzma",
    ) -> Generator[Tuple[str, str], None, None]:
        assert tagset in ("ud", "ptb")
        pos_attr = "upos" if tagset == "ud" else "xpos"

        doc = cls.parse(doc, is_cache=is_cache, cache_path=cache_path, processors=("tokenize", "pos", "lemma"))
        for sent in doc.sentences:
            for word in sent.words:
                yield (word.lemma.lower(), getattr(word, pos_attr))
