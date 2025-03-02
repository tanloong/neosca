#!/usr/bin/env python3

import os

from neosca.ns_nlp import NsNLPStanza

from .base_tmpl import BaseTmpl
from .cmdline_tmpl import text as cli_text


class TestNLPStanza(BaseTmpl):
    def setUp(self):
        self.processors = NsNLPStanza.processors
        return super().setUp()

    def test_private_nlp(self):
        processors = ("tokenize",)
        doc = NsNLPStanza._text2doc(cli_text, processors=processors)
        self.assertSetEqual(doc.processors, set(processors))

        doc2 = NsNLPStanza._text2doc(doc)
        self.assertSetEqual(doc2.processors, set(self.processors))

    def test_nlp(self):
        default_cache_path = "cli_text.pickle.lzma"
        self.assert_file_not_exist(default_cache_path)
        processors = ("tokenize",)
        doc = NsNLPStanza.text2doc(cli_text, processors=processors, cache_path=default_cache_path)
        self.assertSetEqual(doc.processors, set(processors))
        self.assert_file_exists(default_cache_path)
        os.remove(default_cache_path)

        doc2 = NsNLPStanza.text2doc(doc, processors=self.processors)
        self.assertSetEqual(doc2.processors, set(self.processors))
        self.assert_file_not_exist(default_cache_path)

    def test_doc_serialized_conversion(self):
        doc = NsNLPStanza.text2doc(cli_text)
        serialized = NsNLPStanza.doc2serialized(doc)
        doc2 = NsNLPStanza.serialized2doc(serialized)
        self.assertSetEqual(doc.processors, doc2.processors)
