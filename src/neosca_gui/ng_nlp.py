#!/usr/bin/env python3

import pickle
from typing import Optional, Sequence

from stanza import Document


class Ng_NLP_Stanza:
    # Stores all possibly needed processors in the whole application
    processors: tuple = ("tokenize", "pos", "lemma", "constituency")

    @classmethod
    def initialize(cls, lang: Optional[str] = None, model_dir: Optional[str] = None) -> None:
        import stanza

        lang = lang if lang is not None else "en"
        model_dir = model_dir if model_dir is not None else stanza.resources.common.DEFAULT_MODEL_DIR
        cls.pipeline = stanza.Pipeline(
            lang=lang,
            dir=model_dir,
            # TODO: need to (1) choose processors dynamically when initializing
            #       (2) see if possible to drop or load processors after initializing
            # Stanza 1.6.1 does not allow set yet
            processors=cls.processors,
            # https://github.com/stanfordnlp/stanza/issues/331
            resources_url="stanford",
            download_method=None,
        )

    @classmethod
    def nlp(cls, doc, processors: Optional[Sequence[str]] = None) -> Document:
        assert isinstance(doc, (str, Document))

        if not hasattr(cls, "pipeline"):
            cls.initialize()

        doc = cls.pipeline(doc, processors=processors)
        if processors is not None:
            doc.processors = set(processors)
        return doc

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
