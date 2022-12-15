#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import os
import subprocess
import sys


class Parser:
    parser_method = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
    parser_model = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"

    def __init__(self, dir_stanford_parser: str):
        self.classpath = '"' + dir_stanford_parser + os.sep + "*" + '"'

    def parse(self, text: str, ofile_parsed: str) -> str:
        """Call Stanford Parser"""
        print(f"\t[Parser] Parsing...")
        cmd = (
            f'java -mx3g -cp {self.classpath} "{self.parser_method}"'
            f" -outputFormat penn -nthreads 2 {self.parser_model} -"
        )
        try:
            p = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                shell=True,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as err_msg:
            print(err_msg)
            if os.path.exists(ofile_parsed):
                os.remove(ofile_parsed)
            sys.exit(1)
        return p.stdout.decode("utf-8")
