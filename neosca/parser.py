#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import os
import sys

import jpype  # type:ignore


class StanfordParser:
    def __init__(
        self,
        dir_stanford_parser: str,
        newline_break: str,
        max_length: int,
        verbose: bool = False,
        nthreads: int = 1,  # tested on a 16kb file: 3m23s on 2 threads vs. 3m21s on 1 threads
        max_memory: str = "3072m",  # 3g
    ) -> None:
        self.PARSER_PACKAGE = "edu.stanford.nlp"
        self.PARSER_METHOD = "edu.stanford.nlp.parser.lexparser"
        self.PARSER_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
        self.verbose = verbose
        self.newline_break = newline_break
        self.max_length = max_length
        self.parsed_sent_num = 0
        self.long_sent_num = 0
        self.no_parse_num = 0
        self.PROMPT_PARSING = "Parsing [sent. {} len. {}]: {}"
        self.PROMPT_LONG_SENTENCE = "Sentence longer than {}. Skipping: {}\n"
        self.PROMPT_NO_PARSE = (
            'Sentence has no parse using PCFG grammar (or no PCFG fallback). Skipping: "{}"'
        )
        self.PROMPT_LONG_SENTENCE_SUMMARY = "{} sentences are longer than {} and skipped.\n"
        self.PROMPT_NO_PARSE_SUMMARY = (
            "{} sentences have no parse using PCFG grammar (or no PCFG fallback) and are skipped.\n"
        )

        jpype.startJVM(f"-Xmx{max_memory}", classpath=os.path.join(dir_stanford_parser, "*"))
        package = jpype.JPackage(self.PARSER_PACKAGE)
        package_lexparser = jpype.JPackage(self.PARSER_METHOD)
        CoreLabelTokenFactory = package.process.CoreLabelTokenFactory

        self.tokenizerFactory = package.process.PTBTokenizer.factory(CoreLabelTokenFactory(), "")
        self.WordToSentenceProcessor = package.process.WordToSentenceProcessor()
        self.lexparser = package_lexparser.LexicalizedParser.loadModel(self.PARSER_MODEL)
        options = ["-outputFormat", "penn", "-nthreads", str(nthreads)]
        self.lexparser.setOptionFlags(options)

    def parse_sentence(self, sentence) -> str:
        """Parse a single sentence"""
        sentence_length = len(sentence)
        plain_sentence = " ".join(str(w.toString()) for w in sentence)
        is_long = self.max_length is not None and self.max_length < sentence_length
        if is_long:
            self.long_sent_num += 1
            sys.stderr.write(self.PROMPT_LONG_SENTENCE.format(self.max_length, plain_sentence))
            return ""
        self.parsed_sent_num += 1
        print(self.PROMPT_PARSING.format(self.parsed_sent_num, sentence_length, plain_sentence))
        parse = self.lexparser.parseTree(sentence)
        if parse is not None:
            return str(parse.pennString())
        else:
            self.no_parse_num += 1
            print(self.PROMPT_NO_PARSE.format(plain_sentence))
            return ""

    def parse_paragraph(self, paragraph) -> str:
        doc = jpype.java.io.StringReader(jpype.java.lang.String(paragraph))
        tokens = self.tokenizerFactory.getTokenizer(doc).tokenize()
        sentences = self.WordToSentenceProcessor.process(tokens)
        trees = "\n".join(self.parse_sentence(sentence) for sentence in sentences)
        return trees

    def parse(self, text: str) -> str:
        if self.newline_break == "never":
            trees = self.parse_paragraph(text)
        else:
            if self.newline_break == "always":
                paragraphs = list(filter(None, text.split("\n")))
            else:
                import re

                paragraphs = re.split(r"(?:\r?\n){2,}", text)
            trees = "\n".join(self.parse_paragraph(paragraph) for paragraph in paragraphs)
        self.parsed_sent_num = 0
        sys.stderr.write(self.PROMPT_LONG_SENTENCE_SUMMARY.format(self.long_sent_num, self.max_length))
        sys.stderr.write(self.PROMPT_NO_PARSE_SUMMARY.format(self.no_parse_num))
        return trees
