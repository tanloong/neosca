#!/usr/bin/env python3
import logging
import sys
from typing import Optional


class Ns_Stanza:
    def __init__(
        self,
        model_dir: Optional[str] = None,
    ) -> None:
        import stanza

        self.model_dir = model_dir if model_dir is not None else stanza.resources.common.DEFAULT_MODEL_DIR
        logging.debug(f"[NeoSCA] Initializing Stanza with model directory as {model_dir}...")
        self.nlp_stanza = stanza.Pipeline(
            lang="en",
            dir=self.model_dir,
            processors="tokenize,pos,constituency",
            # https://github.com/stanfordnlp/stanza/issues/331
            resources_url="stanford",
            download_method=None,
        )

    def parse(
        self,
        text: str,
        is_reserve_parsed: bool = False,
        ofile_parsed: str = "cmdline_text.parsed",
        is_stdout: bool = False,
    ) -> str:
        doc = self.nlp_stanza(text)
        trees = "\n".join(sent.constituency.pretty_print() for sent in doc.sentences)
        if is_reserve_parsed:
            if not is_stdout:
                with open(ofile_parsed, "w", encoding="utf-8") as f:
                    f.write(trees)
            else:
                sys.stdout.write(trees + "\n")
        return trees
