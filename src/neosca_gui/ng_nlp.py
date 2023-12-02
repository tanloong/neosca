#!/usr/bin/env python3

import logging
import lzma
import pickle
from typing import Generator, Literal, Optional, Sequence, Tuple, Union

from stanza import Document


class Ng_NLP_Stanza:
    # Stores all possibly needed processors in the whole application
    processors: tuple = ("tokenize", "pos", "lemma", "constituency")

    @classmethod
    def initialize(cls, lang: Optional[str] = None, model_dir: Optional[str] = None) -> None:
        import stanza

        if lang is None:
            lang = "en"
        if model_dir is None:
            model_dir = stanza.resources.common.DEFAULT_MODEL_DIR

        cls.pipeline = stanza.Pipeline(
            lang=lang,
            dir=model_dir,
            # TODO: need to (1) choose processors dynamically when initializing
            #       (2) see if possible to drop or load processors after initializing
            processors=cls.processors,
            # https://github.com/stanfordnlp/stanza/issues/331
            resources_url="stanford",
            download_method=None,
        )

    @classmethod
    def _nlp(cls, doc, processors: Optional[Sequence[str]] = None) -> Document:
        assert isinstance(doc, (str, Document))

        if not hasattr(cls, "pipeline"):
            cls.initialize()

        doc = cls.pipeline(doc, processors=processors)
        if processors is not None:
            doc.processors = set(processors)
        return doc

    @classmethod
    def nlp(
        cls,
        doc: Union[str, Document],
        processors: Optional[tuple] = None,
        is_cache: bool = False,
        cache_path: Optional[str] = None,
    ) -> Document:
        if cache_path is None:
            cache_path = "cmdline_text.pickle.lzma"

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

        if has_just_processed and is_cache:
            logging.debug(f"Caching document to {cache_path}")
            with open(cache_path, "wb") as f:
                f.write(lzma.compress(cls.doc2serialized(doc)))
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
        doc = cls.nlp(
            doc, processors=("tokenize", "pos", "constituency"), is_cache=is_cache, cache_path=cache_path
        )
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

        doc = cls.nlp(doc, is_cache=is_cache, cache_path=cache_path, processors=("tokenize", "pos", "lemma"))
        for sent in doc.sentences:
            for word in sent.words:
                yield (word.lemma.lower(), getattr(word, pos_attr))

    @classmethod
    def doc2serialized(cls, doc: Document) -> bytes:
        doc_dict = {"meta_data": {}, "serialized": None}
        doc_dict["serialized"] = doc.to_serialized()

        attr = "processors"
        if hasattr(doc, attr):
            doc_dict["meta_data"][attr] = getattr(doc, attr)
        return pickle.dumps(doc_dict)

    @classmethod
    def serialized2doc(cls, data: bytes) -> Document:
        """
        Specifically for loading documents that were serialized by "doc2serialized"
        """
        doc_dict = pickle.loads(data)
        doc = Document.from_serialized(doc_dict["serialized"])

        attr = "processors"
        if value := doc_dict["meta_data"][attr]:
            setattr(doc, attr, value)
        return doc
