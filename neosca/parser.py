#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import os
import subprocess
import sys


class Parser:
    method_parser = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
    model_parser = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"

    def __init__(self, dir_stanford_parser: str):
        self.classpath = '"' + dir_stanford_parser + os.sep + "*" + '"'

    def parse(self, ifile: str, fn_parsed: str) -> None:
        """
        Call Stanford Parser

        :param ifile: file to parse
        :param fn_parsed: where to save the parsed results
        :return: None
        """
        print(f"\t[Parser] Parsing...")
        cmd = (
            f'java -mx1500m -cp {self.classpath} "{self.method_parser}"'
            f' -outputFormat penn -nthreads -1 {self.model_parser} "{ifile}" >'
            f' "{fn_parsed}"'
        )
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as err_msg:
            print(err_msg)
            if os.path.exists(fn_parsed):
                os.remove(fn_parsed)
            sys.exit(1)
