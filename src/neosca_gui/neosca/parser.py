#!/usr/bin/env python3
import logging
import sys
from typing import Optional

from neosca_gui.ng_nlp import Ng_NLP_Stanza


class Ns_Stanza:
    @classmethod
    def parse(
        cls,
        text: str,
        is_reserve_parsed: bool = False,
        ofile_parsed: str = "cmdline_text.parsed",
        is_stdout: bool = False,
    ) -> str:
        doc = Ng_NLP_Stanza.nlp(text, processors=("tokenize", "pos", "constituency"))
        trees = "\n".join(sent.constituency.pretty_print() for sent in doc.sentences)
        if is_reserve_parsed:
            if not is_stdout:
                with open(ofile_parsed, "w", encoding="utf-8") as f:
                    f.write(trees)
            else:
                sys.stdout.write(trees + "\n")
        return trees
