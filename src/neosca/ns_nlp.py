#!/usr/bin/env python3

import logging
import lzma
import os
import os.path as os_path
import pickle
from collections.abc import Sequence
from typing import Any, Literal

from stanza import Document

from .ns_consts import STANZA_MODEL_DIR
from .ns_io import Ns_Cache, Ns_IO


class Ns_NLP_Stanza:
    # Stores all processors needed in the whole application
    processors: tuple = ("tokenize", "mwt", "pos", "lemma", "constituency")

    @classmethod
    def initialize(cls, lang: str | None = None, model_dir: str | None = None) -> None:
        import stanza

        if lang is None:
            lang = "en"
        if model_dir is None:
            model_dir = str(STANZA_MODEL_DIR)

        logging.debug("Loading Stanza processors...")
        cls.pipeline = stanza.Pipeline(  # type: ignore
            lang=lang,
            dir=model_dir,
            processors=cls.processors,
            verbose=False,
            # https://github.com/stanfordnlp/stanza/issues/331
            resources_url="stanford",
            download_method=None,
        )

    @classmethod
    def _text2doc(cls, doc: str | Document, processors: Sequence[str] | set[str] | None = None) -> Document:
        assert isinstance(doc, (str, Document))

        attr = "pipeline"
        if not hasattr(cls, attr):
            cls.initialize()
        assert hasattr(cls, attr)

        if processors is None:
            processors = cls.processors

        doc = cls.pipeline(doc, processors=processors)  # type: ignore
        doc.processors = set(processors)
        return doc

    @classmethod
    def text2doc(
        cls,
        doc: str | Document,
        processors: Sequence[str] | set[str] | None = None,
        cache_path: str | None = None,
    ) -> Document:
        if processors is None:
            processors = cls.processors

        if isinstance(doc, str):
            logging.debug("Processing bare text...")
            doc = cls._text2doc(doc, processors=processors)
        else:
            attr = "processors"
            existing_processors = set(getattr(doc, attr)) if hasattr(doc, attr) else set()
            filtered_processors = set(processors) - existing_processors
            if not filtered_processors:
                return doc

            logging.debug(
                f"Processing partially parsed document with additional processors {filtered_processors}"
            )
            doc = cls._text2doc(doc, processors=filtered_processors)
            setattr(doc, attr, existing_processors | filtered_processors)

        if cache_path is not None:
            logging.debug(f"Caching document to {cache_path}...")
            Ns_IO.dump_bytes(lzma.compress(cls.doc2serialized(doc)), cache_path)

        return doc

    @classmethod
    def file2doc(
        cls,
        file_path: str,
        *,
        processors: Sequence[str] | set[str] | None = None,
        is_cache: bool = True,
        is_use_cache: bool = True,
    ) -> Document:
        cache_path, is_cache_available = Ns_Cache.get_cache_path(file_path)

        # Use cache
        if is_use_cache and is_cache_available:
            logging.info(f"Loading cache: {cache_path}.")
            doc: Document = Ns_NLP_Stanza.serialized2doc(Ns_IO.load_lzma(cache_path))
            return doc

        # Use raw text
        text = Ns_IO.load_file(file_path)
        if not is_cache:
            cache_path = None
        try:
            doc: Document = Ns_NLP_Stanza.text2doc(text, processors, cache_path)
        except BaseException:
            # If cache is generated at current run, remove it as it is potentially broken
            if cache_path is not None and os_path.exists(cache_path) and not is_cache_available:
                os.remove(cache_path)
            raise
        return doc

    @classmethod
    def doc2tree(cls, doc: Document) -> str:
        return "\n".join(
            str(sent.constituency)
            for sent in doc.sentences
            if not (len(sent.words) == 1 and sent.words[0].upos == "PUNCT")
        )

    @classmethod
    def get_constituency_forest(
        cls,
        doc: str | Document,
        *,
        cache_path: str | None = None,
    ) -> str:
        doc = cls.text2doc(doc, processors=("tokenize", "pos", "constituency"), cache_path=cache_path)
        return cls.doc2tree(doc)

    @classmethod
    def get_lemma_and_pos(
        cls,
        doc: str | Document,
        *,
        tagset: Literal["ud", "ptb"],
        cache_path: str | None = None,
    ) -> tuple[tuple[str, str], ...]:
        """
        For LCA
        """
        if tagset == "ud":
            pos_attr = "upos"
        elif tagset == "ptb":
            pos_attr = "xpos"
        else:
            assert False, "Invalid tagset"

        doc = cls.text2doc(doc, processors=("tokenize", "pos", "lemma"), cache_path=cache_path)
        return tuple(
            # Foreign words could have word.lemma as None
            (word.lemma.lower() if word.lemma is not None else word.text.lower(), getattr(word, pos_attr))
            for sent in doc.sentences
            for word in sent.words
        )

    @classmethod
    def doc2serialized(cls, doc: Document) -> bytes:
        doc_dict: dict[str, Any] = {"meta_data": {}, "serialized": None}
        doc_dict["serialized"] = doc.to_serialized()

        attr = "processors"
        if hasattr(doc, attr):
            doc_dict["meta_data"][attr] = getattr(doc, attr)
        return pickle.dumps(doc_dict)

    @classmethod
    def serialized2doc(cls, data: bytes) -> Document:
        doc_dict = pickle.loads(data)
        doc = Document.from_serialized(doc_dict["serialized"])

        attr = "processors"
        if "meta_data" in doc_dict and attr in doc_dict["meta_data"]:
            setattr(doc, attr, doc_dict["meta_data"][attr])
        return doc
