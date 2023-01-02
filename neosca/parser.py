#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import os
import subprocess
import sys


class Parser:
    PARSER_METHOD = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
    PARSER_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
    NTHREADS = 2
    MAX_MEMORY = "3g"

    def __init__(
        self,
        dir_stanford_parser: str,
        nthreads=NTHREADS,
        max_memory=MAX_MEMORY,
        verbose=False,
    ) -> None:
        self.classpath = '"' + dir_stanford_parser + os.sep + "*" + '"'
        self.max_memory = max_memory
        self.nthreads = nthreads
        self.verbose = verbose

    def parse(self, text: str, ofile_parsed: str) -> str:
        """Call Stanford Parser"""
        cmd = (
            f"java -mx{self.max_memory} -cp"
            f' {self.classpath} "{self.PARSER_METHOD}" -outputFormat penn'
            f" -nthreads {self.nthreads} {self.PARSER_MODEL} -"
        )
        print(f"\t[Parser] Parsing with command '{cmd}'...")
        try:
            p = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=None if self.verbose else subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as err_msg:
            print(err_msg)
            if os.path.exists(ofile_parsed):
                os.remove(ofile_parsed)
            sys.exit(1)
        return p.stdout.decode("utf-8")
