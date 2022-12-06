import argparse
import glob
from os import path
import os
import subprocess
import sys
from typing import List, Optional, Tuple
from itertools import tee

from . import __version__
from .neosca import NeoSCA
from .writer import write_match_output
from .writer import write_freq_output

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
SCAProcedureResult = Tuple[bool, Optional[str]]


class SCAUI:
    def __init__(self):
        self.parser: argparse.ArgumentParser = self.create_parser()
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
            "--list",
            dest="list_fields",
            action="store_true",
            default=False,
            help="list output fields",
        )
        parser.add_argument(
            "-o",
            "--output",
            metavar="OUTFILE",
            dest="ofile_freq",
            default="result.csv",
            help="output file",
        )
        parser.add_argument(
            "--parser",
            dest="dir_stanford_parser",
            default=os.getenv("STANFORD_PARSER_HOME"),
            help=(
                "directory to Stanford Parser, defaults to STANFORD_PARSER_HOME"
            ),
        )
        parser.add_argument(
            "--tregex",
            dest="dir_stanford_tregex",
            default=os.getenv("STANFORD_TREGEX_HOME"),
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
        parser.add_argument(
            "--no-query",
            dest="no_query",
            action="store_true",
            default=False,
            help="just parse input files and exit",
        )
        return parser

    def parse_args(self, argv: List[str]) -> SCAProcedureResult:
        args = argv[1:] if argv[1:] else ["--help"]
        options, ifile_list = self.parser.parse_known_args(args)
        self.odir_match = path.splitext(options.ofile_freq)[0]

        if options.dir_stanford_parser is None:
            return (
                False,
                "You need to either set $STANFORD_PARSER_HOME or give the path"
                " of Stanford Parser through the `--parser` option.",
            )
        if not path.isdir(options.dir_stanford_parser):
            return False, f"{options.dir_stanford_parser} is invalid."

        if options.dir_stanford_tregex is None:
            return (
                False,
                "You need to either set $STANFORD_TREGEX_HOME or give the path"
                " of Stanford Tregex through the `--tregex` option.",
            )
        if not path.isdir(options.dir_stanford_tregex):
            return False, f"{options.dir_stanford_tregex} is invalid."
        if options.no_query:
            options.reserve_parsed = True

        self.options = options

        verified_ifile_list = []
        for f in ifile_list:
            if path.isfile(f):
                verified_ifile_list.append(f)
            elif glob.glob(f):
                verified_ifile_list.extend(glob.glob(f))
            else:
                return (False, f"No such file as \n\n{f}")

        self.init_kwargs = {
            "dir_stanford_parser": options.dir_stanford_parser,
            "dir_stanford_tregex": options.dir_stanford_tregex,
            "ifiles": verified_ifile_list,
            "reserve_parsed": options.reserve_parsed,
        }

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
        analyzer = NeoSCA(**self.init_kwargs)

        if self.options.no_query:
            analyzer.parse_and_exit()
            return True, None
        gen = analyzer.parse_and_query()
        structures_generator1, structures_generator2 = tee(gen, 2)
        # a generator of instances of Structures, each for one corresponding input file

        freq_output = ""
        for structures in structures_generator1:
            freq_output += structures.get_freqs() + "\n"
        write_freq_output(freq_output, self.options.ofile_freq)

        if self.options.reserve_match:
            for structures in structures_generator2:
                write_match_output(structures, self.odir_match)
            print(f"Match output was saved to {path.abspath(self.odir_match)}.")

        return True, None

    def run(self) -> SCAProcedureResult:
        if self.options.version:
            return self.show_version()
        elif self.options.list_fields:
            return self.list_fields()
        else:
            return self.run_analyzer()

    def list_fields(self) -> SCAProcedureResult:
        from .structures import Structures

        field_info = "W: words"
        for structure in Structures.to_report:
            field_info += f"\n{structure.name}: {structure.desc}"
        print(field_info)
        return True, None

    def show_version(self) -> SCAProcedureResult:
        print(__version__)
        return True, None


def main():
    ui = SCAUI()
    success, err_msg = ui.parse_args(sys.argv)
    if not success:
        print(err_msg)
        sys.exit(1)
    success, err_msg = ui.run()
    if not success:
        print(err_msg)
        sys.exit(1)
