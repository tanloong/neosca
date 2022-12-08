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
        self.args_parser: argparse.ArgumentParser = self.create_args_parser()
        self.options: argparse.Namespace = argparse.Namespace()

    def create_args_parser(self) -> argparse.ArgumentParser:
        args_parser = argparse.ArgumentParser(
            prog="nsca",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=50, width=100
            ),
        )
        args_parser.add_argument(
            "--version",
            action="store_true",
            default=False,
            help="show version of NeoSCA",
        )
        args_parser.add_argument(
            "--list",
            dest="list_fields",
            action="store_true",
            default=False,
            help="list output fields",
        )
        args_parser.add_argument(
            "--text",
            "-t",
            default=None,
            help="pass text through command line",
        )
        args_parser.add_argument(
            "--output",
            "-o",
            metavar="OUTFILE",
            dest="ofile_freq",
            default="result.csv",
            help="output file",
        )
        args_parser.add_argument(
            "--no-query",
            dest="no_query",
            action="store_true",
            default=False,
            help="just parse input files, save parsed trees, and exit",
        )
        args_parser.add_argument(
            "--parser",
            dest="dir_stanford_parser",
            default=os.getenv("STANFORD_PARSER_HOME"),
            help=(
                "directory to Stanford Parser, defaults to STANFORD_PARSER_HOME"
            ),
        )
        args_parser.add_argument(
            "--tregex",
            dest="dir_stanford_tregex",
            default=os.getenv("STANFORD_TREGEX_HOME"),
            help=(
                "directory to Stanford Tregex, defaults to STANFORD_TREGEX_HOME"
            ),
        )
        args_parser.add_argument(
            "--reserve-parsed",
            "-p",
            dest="reserve_parsed",
            action="store_true",
            default=False,
            help="option to reserve parsed trees by Stanford Parser",
        )
        args_parser.add_argument(
            "--reserve-matched",
            "-m",
            dest="reserve_matched",
            default=False,
            action="store_true",
            help="option to reserve matched subtrees by Stanford Tregex",
        )
        return args_parser

    def parse_args(self, argv: List[str]) -> SCAProcedureResult:
        options, ifile_list = self.args_parser.parse_known_args(argv[1:])
        self.odir_match = path.splitext(options.ofile_freq)[0] + "_matches"

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

        if options.text is None:
            verified_ifile_list = []
            for f in ifile_list:
                if path.isfile(f):
                    verified_ifile_list.append(f)
                elif glob.glob(f):
                    verified_ifile_list.extend(glob.glob(f))
                else:
                    return (False, f"No such file as \n\n{f}")
        else:
            print("Command-line text is given, input files will be ignored.")
            verified_ifile_list = None
        self.verified_ifile_list = verified_ifile_list

        self.init_kwargs = {
            "dir_stanford_parser": options.dir_stanford_parser,
            "dir_stanford_tregex": options.dir_stanford_tregex,
            "reserve_parsed": options.reserve_parsed,
        }
        self.options = options
        return True, None

    def check_java(self) -> SCAProcedureResult:
        try:
            subprocess.run(
                "java -version", shell=True, check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            return (
                False,
                "Error: Java is unavailable.\n\n1. To install it, visit"
                " https://www.java.com/en/download.\n2. After installing,"
                " make sure you can access it in the cmd window by typing"
                " in `java -version`.",
            )
        return True, None

    def exit_routine(self):
        print("=" * 60)
        i = 1
        if not self.options.no_query:
            print(
                f"{i}. Frequency output was saved to"
                f" {path.abspath(self.options.ofile_freq)}."
            )
            i += 1
        if self.verified_ifile_list and self.options.reserve_parsed:
            print(
                f"{i}. Parsed trees were saved corresponding to input files,"
                ' with the same name but a ".parsed" extension.'
            )
            i += 1
        if self.options.text is not None and self.options.reserve_parsed:
            print(f"{i}. Parsed trees were saved to cmdline_text.parsed.")
            i += 1
        if self.options.reserve_matched:
            print(
                f"{i}. Matched subtrees were saved to"
                f" {path.abspath(self.odir_match)}."
            )
            i += 1
        print("Done.")

    def run_tmpl(func):
        def wrapper(self, *args, **kwargs):
            sucess, err_msg = self.check_java()
            if not sucess:
                return sucess, err_msg
            func(self, *args, **kwargs)
            self.exit_routine()
            return True, None

        return wrapper

    @run_tmpl
    def run_parse_text(self):
        analyzer = NeoSCA(**self.init_kwargs)
        analyzer.parse_text(self.options.text)

    @run_tmpl
    def run_parse_text_and_query(self):
        analyzer = NeoSCA(**self.init_kwargs)
        structures = analyzer.parse_text_and_query(self.options.text)

        freq_output = structures.get_freqs() + "\n"
        write_freq_output(freq_output, self.options.ofile_freq)

        if self.options.reserve_matched:
            write_match_output(structures, self.odir_match)

    @run_tmpl
    def run_parse_ifiles(self):
        analyzer = NeoSCA(**self.init_kwargs)
        analyzer.parse_ifiles(self.verified_ifile_list)

    @run_tmpl
    def run_parse_ifiles_and_query(self):
        analyzer = NeoSCA(**self.init_kwargs)
        gen = analyzer.parse_ifiles_and_query(self.verified_ifile_list)
        structures_generator1, structures_generator2 = tee(gen, 2)
        # a generator of instances of Structures, each for one corresponding input file

        freq_output = ""
        for structures in structures_generator1:
            freq_output += structures.get_freqs() + "\n"
        write_freq_output(freq_output, self.options.ofile_freq)

        if self.options.reserve_matched:
            for structures in structures_generator2:
                write_match_output(structures, self.odir_match)

    def run(self) -> SCAProcedureResult:
        if self.options.version:
            return self.show_version()
        elif self.options.list_fields:
            return self.list_fields()
        elif self.options.text is not None and self.options.no_query:
            return self.run_parse_text()
        elif self.options.text is not None and not self.options.no_query:
            return self.run_parse_text_and_query()
        elif self.verified_ifile_list and self.options.no_query:
            return self.run_parse_ifiles()
        elif self.verified_ifile_list and not self.options.no_query:
            return self.run_parse_ifiles_and_query()
        else:
            self.args_parser.print_help()
            return True, None

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
