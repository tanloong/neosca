import argparse
import glob
from os import path
import os
import sys
from typing import List

from . import __version__
from .utils.analyzer import Analyzer
from .utils.writer import write_match_output
from .utils.writer import write_freq_output


class UI:
    def __init__(self):
        self.parser = self.create_parser()

        self.ifile_list = []
        self.ofile_freq = "result.csv"
        self.dir_stanford_parser = os.getenv("STANFORD_PARSER_HOME")
        self.dir_stanford_tregex = os.getenv("STANFORD_TREGEX_HOME")
        self.reserve_parsed = False
        self.reserve_match = False

        self.options: argparse.Namespace = argparse.Namespace()

    def create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="nl2sca",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=30, width=100
            ),
        )
        parser.add_argument(
            "--version",
            action="store_true",
            default=False,
            help="show version of NeoL2SCA",
        )
        parser.add_argument(
            "input",
            nargs="+",
            default=None,
            help="one or more input files",
        )
        parser.add_argument(
            "-o",
            "--output",
            default=None,
            help="output filename",
        )
        parser.add_argument(
            "--parser",
            dest="dir_stanford_parser",
            default=None,
            help=("directory to Stanford Parser, defaults to STANFORD_PARSER_HOME"),
        )
        parser.add_argument(
            "--tregex",
            dest="dir_stanford_tregex",
            default=None,
            help=("directory to Tregex, defaults to STANFORD_TREGEX_HOME"),
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
            help="option to reserve match results by Tregex",
        )
        return parser

    def parse(self, argv: List[str]):
        options, command = self.parser.parse_known_args(argv[1:])

        if options.input:
            self.ifile_list = options.input
        else:
            return False, "Input files are not provided."
        valid_ifile_list = []
        for f in self.ifile_list:
            if path.isfile(f):
                valid_ifile_list.append(f)
            elif glob.glob(f):
                valid_ifile_list.extend(glob.glob(f))
            else:
                return (
                    False,
                    f"The following file either does not exist or is not a regular file: \n\n{f}",
                )
        self.ifile_list = valid_ifile_list

        if options.output:
            self.ofile_freq = options.output
        self.odir_match = path.splitext(self.ofile_freq)[0]

        if options.dir_stanford_parser:
            self.dir_stanford_parser = options.dir_stanford_parser
        if self.dir_stanford_parser is None or not path.isdir(self.dir_stanford_parser):
            return False, "Stanford Parser not found."

        if options.dir_stanford_tregex:
            self.dir_stanford_tregex = options.dir_stanford_tregex
        if self.dir_stanford_tregex is None or not path.isdir(self.dir_stanford_tregex):
            return False, "Stanford Tregex not found."

        if options.reserve_parsed:
            self.reserve_parsed = options.reserve_parsed
        if options.reserve_match:
            self.reserve_match = options.reserve_match
        self.options, self.command = options, command
        return True, None

    def run_analyzer(self):
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

    def run(self):
        if self.options.version:
            return self.show_version()
        else:
            return self.run_analyzer()

    def show_version(self):
        print(__version__)
        return True, None


def main():
    ui = UI()
    success, err_msg = ui.parse(sys.argv)
    if not success:
        print(err_msg)
        sys.exit(1)
    success, err_msg = ui.run()
    if not success:
        print(err_msg)
        sys.exit(1)
