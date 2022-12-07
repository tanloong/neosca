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

    def parse(self, fn_parsed:str, ifile=None, text=None) -> str:
        """ Call Stanford Parser """
        print(f"\t[Parser] Parsing...")
        cmd_base = (
            f'java -mx1500m -cp {self.classpath} "{self.method_parser}"'
            f" -outputFormat penn -nthreads -1 {self.model_parser} "
        )

        if text is not None:
            cmd = cmd_base + "-"
            input = text.encode("utf-8")
        elif ifile is not None:
            cmd = cmd_base + f'"{ifile}"'
            input = None
        else:
            print("Neither {ifile} nor {text} is provided.")
            sys.exit(1)
        try:
            p = subprocess.run(
                cmd,
                input=input,
                shell=True,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as err_msg:
            print(err_msg)
            if os.path.exists(fn_parsed):
                os.remove(fn_parsed)
            sys.exit(1)
        return p.stdout.decode("utf-8")
