#!/usr/bin/env python3

import logging
import lzma
import pickle
from typing import Any, Dict, Literal, Optional, Sequence, Tuple, Union

from stanza import Document

from neosca import STANZA_MODEL_DIR
from neosca.ns_io import Ns_IO


class Ns_NLP_Stanza:
    # Stores all processors needed in the whole application
    processors: tuple = ("tokenize", "mwt", "pos", "lemma", "constituency")

    @classmethod
    def initialize(cls, lang: Optional[str] = None, model_dir: Optional[str] = None) -> None:
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
    def _nlp(cls, doc, processors: Optional[Sequence[str]] = None) -> Document:
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
    def nlp(
        cls,
        doc: Union[str, Document],
        processors: Optional[tuple] = None,
        cache_path: Optional[str] = None,
    ) -> Document:
        has_just_processed: bool = False

        if processors is None:
            processors = cls.processors

        if isinstance(doc, str):
            logging.debug("Processing bare text...")
            doc = cls._nlp(doc, processors=processors)
            has_just_processed = True
        else:
            attr = "processors"
            existing_processors = set(getattr(doc, attr)) if hasattr(doc, attr) else set()
            filtered_processors = set(processors) - existing_processors
            if filtered_processors:
                logging.debug(
                    f"Processing partially parsed document with additional processors {filtered_processors}"
                )
                doc = cls._nlp(doc, processors=tuple(filtered_processors))
                setattr(doc, attr, existing_processors | filtered_processors)
                has_just_processed = True

        if has_just_processed and cache_path is not None:
            logging.debug(f"Caching document to {cache_path}...")
            Ns_IO.dump_bytes(lzma.compress(cls.doc2serialized(doc)), cache_path)

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
        doc: Union[str, Document],
        *,
        cache_path: Optional[str] = None,
    ) -> str:
        doc = cls.nlp(doc, processors=("tokenize", "pos", "constituency"), cache_path=cache_path)
        return cls.doc2tree(doc)

    @classmethod
    def get_lemma_and_pos(
        cls,
        doc: Union[str, Document],
        *,
        tagset: Literal["ud", "ptb"],
        cache_path: Optional[str] = None,
    ) -> Tuple[Tuple[str, str], ...]:
        if tagset == "ud":
            pos_attr = "upos"
        elif tagset == "ptb":
            pos_attr = "xpos"
        else:
            assert False, "Invalid tagset"

        doc = cls.nlp(doc, processors=("tokenize", "pos", "lemma"), cache_path=cache_path)
        return tuple(
            # Foreign words could have word.lemma as None
            (word.lemma.lower() if word.lemma is not None else word.text.lower(), getattr(word, pos_attr))
            for sent in doc.sentences
            for word in sent.words
        )

    @classmethod
    def doc2serialized(cls, doc: Document) -> bytes:
        doc_dict: Dict[str, Any] = {"meta_data": {}, "serialized": None}
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
