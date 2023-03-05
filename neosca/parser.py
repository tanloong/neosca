#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import os
import sys
from typing import Optional

import jpype  # type:ignore
from jpype import JClass


class StanfordParser:
    def __init__(
        self,
        dir_stanford_parser: str = "",
        is_verbose: bool = False,
        nthreads: int = 1,
        # tested on a 16kb file: 3m23s with 2 threads vs. 3m21s with 1 threads
        max_memory: str = "3072m",  # 3g
    ) -> None:
        self.dir_stanford_parser = dir_stanford_parser
        self.is_verbose = is_verbose
        self.nthreads = nthreads
        self.max_memory = max_memory

        self.PARSER_GRAMMAR = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
        self.PARSER_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
        self.parsed_sent_num = 0
        self.long_sent_num = 0
        self.no_parse_num = 0
        self.PROMPT_PARSING = "Parsing [sent. {} len. {}]: {}"
        self.PROMPT_LONG_SENTENCE = "Sentence longer than {}. Skipping: {}\n"
        self.PROMPT_NO_PARSE = (
            'Sentence has no parse using PCFG grammar (or no PCFG fallback). Skipping: "{}"'
        )
        self.PROMPT_LONG_SENTENCE_SUMMARY = (
            "{} sentences are skipped because they are longer than {}.\n"
        )
        self.PROMPT_NO_PARSE_SUMMARY = (
            "{} sentences are skipped because they have no parse using PCFG grammar (or no PCFG"
            " fallback).\n"
        )
        self.init_parser()

    def init_parser(self):
        classpath = os.path.join(self.dir_stanford_parser, "*")
        if not jpype.isJVMStarted():
            # Note that isJVMStarted may be renamed to isJVMRunning in the future.
            # In jpype's _core.py:
            # > TODO This method is horribly named.  It should be named isJVMRunning as
            # > isJVMStarted would seem to imply that the JVM was started at some
            # > point without regard to whether it has been shutdown.
            jpype.startJVM(f"-Xmx{self.max_memory}", classpath=classpath)
        else:
            jpype.addClassPath(classpath)

        LexicalizedParser = JClass(self.PARSER_GRAMMAR)
        self.lp = LexicalizedParser.loadModel(self.PARSER_MODEL)
        options = ["-outputFormat", "penn", "-nthreads", str(self.nthreads)]
        self.lp.setOptionFlags(options)

    def _is_long(self, sentence_length: int, max_length: Optional[int] = None) -> bool:
        if max_length is not None and max_length < sentence_length:
            return True
        return False

    def parse_sentence(self, sentence, max_length: Optional[int] = None) -> str:
        """Parse a single sentence"""
        sentence_length = len(sentence)
        plain_sentence = " ".join(str(w.toString()) for w in sentence)
        if self._is_long(sentence_length, max_length):
            self.long_sent_num += 1
            sys.stderr.write(self.PROMPT_LONG_SENTENCE.format(max_length, plain_sentence))
            return ""
        self.parsed_sent_num += 1
        print(self.PROMPT_PARSING.format(self.parsed_sent_num, sentence_length, plain_sentence))
        parse = self.lp.apply(sentence)
        if parse is not None:
            return str(parse.pennString().replaceAll("\r", ""))
        else:
            self.no_parse_num += 1
            print(self.PROMPT_NO_PARSE.format(plain_sentence))
            return ""

    def parse_paragraph(self, paragraph: str, max_length: Optional[int] = None) -> str:
        doc = JClass("edu.stanford.nlp.process.DocumentPreprocessor")(
            jpype.java.io.StringReader(paragraph)
        )
        trees = "\n".join(self.parse_sentence(sentence, max_length) for sentence in doc)
        return trees

    def refresh_counters(self, max_length: Optional[int] = None) -> None:
        if max_length is not None:
            sys.stderr.write(
                self.PROMPT_LONG_SENTENCE_SUMMARY.format(self.long_sent_num, max_length)
            )
        sys.stderr.write(self.PROMPT_NO_PARSE_SUMMARY.format(self.no_parse_num))
        self.parsed_sent_num = 0
        self.long_sent_num = 0
        self.no_parse_num = 0

    def parse(
        self, text: str, max_length: Optional[int] = None, newline_break: str = "never"
    ) -> str:
        assert newline_break in ("never", "always", "two")
        if newline_break == "never":
            trees = self.parse_paragraph(text, max_length)
        else:
            if newline_break == "always":
                paragraphs = list(filter(None, text.split("\n")))
            else:
                import re

                paragraphs = re.split(r"(?:\r?\n){2,}", text)
            trees = "\n".join(self.parse_paragraph(paragraph) for paragraph in paragraphs)
        self.refresh_counters(max_length)
        return trees
