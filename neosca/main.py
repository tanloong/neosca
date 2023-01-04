import argparse
import glob
from itertools import tee
from os import path
import os
import subprocess
import sys
from typing import List, Optional, Tuple

from . import __version__
from .neosca import NeoSCA
from .writer import write_match_output
from .writer import write_freq_output
from .util import color_print

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
SCAProcedureResult = Tuple[bool, Optional[str]]


class SCAUI:
    def __init__(self) -> None:
        self.args_parser: argparse.ArgumentParser = self.create_args_parser()
        self.options: argparse.Namespace = argparse.Namespace()
        self.cwd = os.getcwd()

    def create_args_parser(self) -> argparse.ArgumentParser:
        args_parser = argparse.ArgumentParser(prog="nsca")
        args_parser.add_argument(
            "--version",
            action="store_true",
            default=False,
            help="show the version of NeoSCA",
        )
        args_parser.add_argument(
            "--list",
            dest="list_fields",
            action="store_true",
            default=False,
            help="list the available output fields",
        )
        args_parser.add_argument(
            "--text",
            "-t",
            default=None,
            help="pass text through the command line",
        )
        args_parser.add_argument(
            "--output-file",
            "-o",
            metavar="OUTFILE",
            dest="ofile_freq",
            default=None,
            help="specify an output file",
        )
        args_parser.add_argument(
            "--output-format",
            dest="oformat_freq",
            choices=["csv", "json"],
            default="csv",
            help="output format, the default is csv",
        )
        args_parser.add_argument(
            "--stdout",
            dest="stdout",
            action="store_true",
            default=False,
            help=(
                "write the frequency output to the stdout instead of saving it to a file"
            ),
        )
        args_parser.add_argument(
            "--parser",
            dest="dir_stanford_parser",
            default=os.getenv("STANFORD_PARSER_HOME"),
            help=(
                "specify the path to Stanford Parser, the default is the value"
                " of STANFORD_PARSER_HOME"
            ),
        )
        args_parser.add_argument(
            "--tregex",
            dest="dir_stanford_tregex",
            default=os.getenv("STANFORD_TREGEX_HOME"),
            help=(
                "specify the path to Stanford Tregex, the default is the value"
                " of STANFORD_TREGEX_HOME"
            ),
        )
        args_parser.add_argument(
            "--reserve-parsed",
            "-p",
            dest="reserve_parsed",
            action="store_true",
            default=False,
            help="reserve the parsed trees produced by the Stanford Parser",
        )
        args_parser.add_argument(
            "--reserve-matched",
            "-m",
            dest="reserve_matched",
            default=False,
            action="store_true",
            help="reserve the matched subtrees produced by the Stanford Tregex",
        )
        args_parser.add_argument(
            "--no-query",
            dest="no_query",
            action="store_true",
            default=False,
            help="parse the input files, save the parsed trees, and exit",
        )
        args_parser.add_argument(
            "--verbose",
            action="store_true",
            default=False,
            help="print detailed log messages",
        )
        return args_parser

    def parse_args(self, argv: List[str]) -> SCAProcedureResult:
        options, ifile_list = self.args_parser.parse_known_args(argv[1:])

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
            print(f"Command-line text: {options.text}")
            verified_ifile_list = None
        self.verified_ifile_list = verified_ifile_list

        self.odir_match = "result_matches"
        if options.stdout:
            options.ofile_freq = sys.stdout
        elif options.ofile_freq is not None:
            self.odir_match = os.path.splitext(options.ofile_freq)[0] + "_matches"
            ofile_freq_ext = os.path.splitext(options.ofile_freq)[-1].lstrip(".")
            if ofile_freq_ext not in ("csv", "json"):
                return (
                    False,
                    f"The file extension {ofile_freq_ext} is not supported. Use one of"
                    " the following:\n1. csv\n2. json",
                )
            if ofile_freq_ext != options.oformat_freq:
                options.oformat_freq = ofile_freq_ext
        else:
            options.ofile_freq = "result." + options.oformat_freq

        self.init_kwargs = {
            "dir_stanford_parser": options.dir_stanford_parser,
            "dir_stanford_tregex": options.dir_stanford_tregex,
            "reserve_parsed": options.reserve_parsed,
            "verbose": options.verbose,
        }
        self.options = options
        return True, None

    def check_java(self) -> SCAProcedureResult:
        try:
            subprocess.run("java -version", shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            return (
                False,
                "Error: Java is unavailable.\n\n1. To install it, visit"
                " https://www.java.com/en/download.\n2. After installing,"
                " make sure you can access it in the cmd window by typing"
                " in `java -version`.",
            )
        return True, None

    def exit_routine(self) -> None:
        print("\n", "=" * 60, sep="")
        i = 1
        if not self.options.no_query and not self.options.stdout:
            print(f"{i}. Frequency output was saved to", end=" ")
            color_print("OKGREEN", f"{path.abspath(self.options.ofile_freq)}", end=".\n")
            i += 1
        if self.verified_ifile_list and self.options.reserve_parsed:
            print(
                f"{i}. Parsed trees were saved corresponding to input files,"
                ' with the same name but a ".parsed" extension.'
            )
            i += 1
        if self.options.text is not None and self.options.reserve_parsed:
            print(f"{i}. Parsed trees were saved to", end=" ")
            color_print("OKGREEN", f"{self.cwd}{os.sep}cmdline_text.parsed", end=".\n")
            i += 1
        if self.options.reserve_matched:
            print(f"{i}. Matched subtrees were saved to", end=" ")
            color_print("OKGREEN", f"{path.abspath(self.odir_match)}", end=".\n")
            i += 1
        print("Done.")

    def run_tmpl(func):  # type: ignore
        def wrapper(self, *args, **kwargs):
            sucess, err_msg = self.check_java()
            if not sucess:
                return sucess, err_msg
            func(self, *args, **kwargs)  # type: ignore
            self.exit_routine()
            return True, None

        return wrapper

    @run_tmpl  # type: ignore
    def run_parse_text(self) -> None:
        analyzer = NeoSCA(**self.init_kwargs)
        analyzer.parse_text(self.options.text)

    @run_tmpl  # type: ignore
    def run_parse_text_and_query(self) -> None:
        analyzer = NeoSCA(**self.init_kwargs)
        structures = analyzer.parse_text_and_query(self.options.text)

        write_freq_output(
            [structures], self.options.ofile_freq, self.options.oformat_freq
        )

        if self.options.reserve_matched:
            write_match_output(structures, self.odir_match)

    @run_tmpl  # type: ignore
    def run_parse_ifiles(self) -> None:
        analyzer = NeoSCA(**self.init_kwargs)
        analyzer.parse_ifiles(self.verified_ifile_list)

    @run_tmpl  # type: ignore
    def run_parse_ifiles_and_query(self) -> None:
        analyzer = NeoSCA(**self.init_kwargs)
        gen = analyzer.parse_ifiles_and_query(self.verified_ifile_list)
        structures_generator1, structures_generator2 = tee(gen, 2)
        # a generator of instances of Structures, each for one corresponding input file

        write_freq_output(
            structures_generator1,
            self.options.ofile_freq,
            self.options.oformat_freq,
        )

        if self.options.reserve_matched:
            for structures in structures_generator2:
                write_match_output(structures, self.odir_match)

    def run(self) -> SCAProcedureResult:
        if self.options.version:
            return self.show_version()
        elif self.options.list_fields:
            return self.list_fields()
        elif self.options.text is not None and self.options.no_query:
            return self.run_parse_text()  # type: ignore
        elif self.options.text is not None and not self.options.no_query:
            return self.run_parse_text_and_query()  # type: ignore
        elif self.verified_ifile_list and self.options.no_query:
            return self.run_parse_ifiles()  # type: ignore
        elif self.verified_ifile_list and not self.options.no_query:
            return self.run_parse_ifiles_and_query()  # type: ignore
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


def main() -> None:
    ui = SCAUI()
    success, err_msg = ui.parse_args(sys.argv)
    if not success:
        print(err_msg)
        sys.exit(1)
    success, err_msg = ui.run()
    if not success:
        print(err_msg)
        sys.exit(1)
