#!/usr/bin/env python3

from typing import Optional


class Ng_NLP_Stanza:
    @classmethod
    def initialize(cls, lang: Optional[str] = None, model_dir: Optional[str] = None) -> None:
        import stanza

        lang = lang if lang is not None else "en"
        model_dir = model_dir if model_dir is not None else stanza.resources.common.DEFAULT_MODEL_DIR
        cls.pipeline = stanza.Pipeline(
            lang=lang,
            dir=model_dir,
            # TODO: need to (1) choose processors dynamically when initializing
            # (2) see if possible to drop or load processors after initializing
            processors="tokenize,pos,constituency",
            # https://github.com/stanfordnlp/stanza/issues/331
            resources_url="stanford",
            download_method=None,
        )

    @classmethod
    def nlp(cls, text: str):
        if not hasattr(cls, "pipeline"):
            cls.initialize()
        return cls.pipeline(text)
