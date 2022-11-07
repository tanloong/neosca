import argparse
import glob
from os import path
import os
import subprocess
import sys
from typing import List, Optional, Tuple

from . import __version__
from .utils.analyzer import Analyzer
from .utils.writer import write_match_output
from .utils.writer import write_freq_output

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
SCAProcedureResult = Tuple[bool, Optional[str]]


class SCAUI:
    def __init__(self):
        self.parser: argparse.ArgumentParser = self.create_parser()

        self.ofile_freq: str = "result.csv"
        self.dir_stanford_parser: Optional[str] = os.getenv(
            "STANFORD_PARSER_HOME"
        )
        self.dir_stanford_tregex: Optional[str] = os.getenv(
            "STANFORD_TREGEX_HOME"
        )
        self.reserve_parsed: bool = False
        self.reserve_match: bool = False

        self.options: argparse.Namespace = argparse.Namespace()

    def create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="nsca",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=50, width=100
            ),
        )
        parser.add_argument(
            "--version",
            action="store_true",
            default=False,
            help="show version of NeoSCA",
        )
        parser.add_argument(
            "-o",
            "--output",
            default=None,
            help="output file",
        )
        parser.add_argument(
            "--parser",
            dest="dir_stanford_parser",
            default=None,
            help=(
                "directory to Stanford Parser, defaults to STANFORD_PARSER_HOME"
            ),
        )
        parser.add_argument(
            "--tregex",
            dest="dir_stanford_tregex",
            default=None,
            help=(
                "directory to Stanford Tregex, defaults to STANFORD_TREGEX_HOME"
            ),
        )
        parser.add_argument(
            "-p",
            "--reserve-parsed",
            dest="reserve_parsed",
            action="store_true",
            default=False,
            help="option to reserve parsed files by Stanford Parser",
        )
        parser.add_argument(
            "-m",
            "--reserve-match",
            dest="reserve_match",
            default=False,
            action="store_true",
            help="option to reserve match results by Stanford Tregex",
        )
        return parser

    def parse(self, argv: List[str]) -> SCAProcedureResult:
        args = argv[1:] if argv[1:] else ["--help"]
        options, ifile_list = self.parser.parse_known_args(args)

        if options.output:
            self.ofile_freq = options.output
        self.odir_match = path.splitext(self.ofile_freq)[0]

        if options.dir_stanford_parser:
            self.dir_stanford_parser = options.dir_stanford_parser
        if self.dir_stanford_parser is None or not path.isdir(
            self.dir_stanford_parser
        ):
            return False, "Stanford Parser not found."

        if options.dir_stanford_tregex:
            self.dir_stanford_tregex = options.dir_stanford_tregex
        if self.dir_stanford_tregex is None or not path.isdir(
            self.dir_stanford_tregex
        ):
            return False, "Stanford Tregex not found."

        if options.reserve_parsed:
            self.reserve_parsed = options.reserve_parsed
        if options.reserve_match:
            self.reserve_match = options.reserve_match

        self.options, self.ifile_list = options, ifile_list

        valid_ifile_list = []
        for f in self.ifile_list:
            if path.isfile(f):
                valid_ifile_list.append(f)
            elif glob.glob(f):
                valid_ifile_list.extend(glob.glob(f))
            else:
                return (False, f"No such file as \n\n{f}")
        self.ifile_list = valid_ifile_list

        return True, None

    def _has_java(self) -> bool:
        try:
            subprocess.run(
                "java -version", shell=True, check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            return False
        return True

    def run_analyzer(self) -> SCAProcedureResult:
        if not self._has_java():
            return (
                False,
                "Error: Java is unavailable.\n\n1. To install it, visit"
                " https://www.java.com/en/download.\n2. After installing, make"
                " sure you can access it in the cmd window by typing in `java"
                " -version`.",
            )
        if not self.ifile_list:
            return False, "Input files are not provided."
        analyzer = Analyzer(self.dir_stanford_parser, self.dir_stanford_tregex)
        structures_list = list(
            analyzer.perform_analysis(self.ifile_list, self.reserve_parsed)
        )  # list of instances of Structures, each for one corresponding input file

        freq_output = ""
        for structures in structures_list:
            freq_output += structures.get_freqs() + "\n"
        write_freq_output(freq_output, self.ofile_freq)

        if self.reserve_match:
            for structures in structures_list:
                write_match_output(structures, self.odir_match)

        return True, None

    def run(self) -> SCAProcedureResult:
        if self.options.version:
            return self.show_version()
        else:
            return self.run_analyzer()

    def show_version(self) -> SCAProcedureResult:
        print(__version__)
        return True, None


def main():
    ui = SCAUI()
    success, err_msg = ui.parse(sys.argv)
    if not success:
        print(err_msg)
        sys.exit(1)
    success, err_msg = ui.run()
    if not success:
        print(err_msg)
        sys.exit(1)
