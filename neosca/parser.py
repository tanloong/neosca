#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import os
import subprocess
import sys


class Parser:
    PARSER_METHOD = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
    PARSER_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
    NTHREADS = "2"
    MAX_MEMORY = "3g"

    def __init__(
        self,
        dir_stanford_parser: str,
        nthreads=NTHREADS,
        max_memory=MAX_MEMORY,
        verbose=False,
    ) -> None:
        self.classpath = dir_stanford_parser + os.sep + "*"
        self.max_memory = max_memory
        self.nthreads = nthreads
        self.verbose = verbose

    def parse(self, text: str, ofile_parsed: str) -> str:
        """Call Stanford Parser"""
        cmd = [
            "java",
            f"-mx{self.max_memory}",
            "-cp",
            self.classpath,
            self.PARSER_METHOD,
            "-outputFormat",
            "penn",
            "-nthreads",
            self.nthreads,
            self.PARSER_MODEL,
            "-",
        ]
        print(f"\t[Parser] Parsing with command ", " ".join(cmd), "...", sep="")
        try:
            p = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                check=True,
                stdout=subprocess.PIPE,
                stderr=None if self.verbose else subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as err_msg:
            print(err_msg)
            if os.path.exists(ofile_parsed):
                os.remove(ofile_parsed)
            sys.exit(1)
        return p.stdout.decode("utf-8")
