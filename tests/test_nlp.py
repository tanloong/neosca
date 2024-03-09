#!/usr/bin/env python3

import os

from neosca.ns_nlp import Ns_NLP_Stanza

from .base_tmpl import BaseTmpl
from .cmdline_tmpl import text as cli_text


class TestNLPStanza(BaseTmpl):
    def setUp(self):
        self.processors = Ns_NLP_Stanza.processors
        return super().setUp()

    def test_private_nlp(self):
        processors = ("tokenize",)
        doc = Ns_NLP_Stanza._nlp(cli_text, processors=processors)
        self.assertSetEqual(doc.processors, set(processors))

        doc2 = Ns_NLP_Stanza._nlp(doc)
        self.assertSetEqual(doc2.processors, set(self.processors))

    def test_nlp(self):
        default_cache_path = "cli_text.pickle.lzma"
        self.assertFileNotExist(default_cache_path)
        processors = ("tokenize",)
        doc = Ns_NLP_Stanza.nlp(cli_text, processors=processors, cache_path=default_cache_path)
        self.assertSetEqual(doc.processors, set(processors))
        self.assertFileExists(default_cache_path)
        os.remove(default_cache_path)

        doc2 = Ns_NLP_Stanza.nlp(doc, processors=self.processors)
        self.assertSetEqual(doc2.processors, set(self.processors))
        self.assertFileNotExist(default_cache_path)

    def test_doc_serialized_conversion(self):
        doc = Ns_NLP_Stanza.nlp(cli_text)
        serialized = Ns_NLP_Stanza.doc2serialized(doc)
        doc2 = Ns_NLP_Stanza.serialized2doc(serialized)
        self.assertSetEqual(doc.processors, doc2.processors)
