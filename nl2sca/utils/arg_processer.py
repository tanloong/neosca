import argparse

# import glob
from os import path
import os
import sys


class ArgProcessor:
    def get_args(self):
        my_argparser = argparse.ArgumentParser(
            description=(
                "Description: perform syntactic complexity analysis of "
                "written English language samples"
            ),
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=30, width=100
            ),
            prog="python -m nl2sca",
        )
        my_argparser.add_argument(
            "fn_inputs",
            type=str,
            nargs="+",
            help="one or more input files",
        )
        my_argparser.add_argument(
            "fn_freq_output",
            type=str,
            help="output filename",
        )
        my_argparser.add_argument(
            "--parser",
            type=str,
            dest="dir_parser",
            help=(
                "directory to Stanford Parser, defaults to"
                # " <parent_dir_of_this_script>/src/stanford-parser-*"
                " STANFORD_PARSER_HOME"
            ),
        )
        my_argparser.add_argument(
            "--tregex",
            type=str,
            dest="dir_tregex",
            help=(
                "directory to Tregex, defaults to"
                # " <parent_dir_of_this_script>/src/stanford-tregex-*"
                " STANFORD_TREGEX_HOME"
            ),
        )
        my_argparser.add_argument(
            "-rp",
            "--reserve-parsed",
            dest="is_reserve_parsed",
            action="store_true",
            help="option to reserve parsed files by Stanford Parser",
        )
        my_argparser.add_argument(
            "-rm",
            "--reserve-match",
            dest="is_reserve_match",
            action="store_true",
            help="option to reserve match results by Tregex",
        )
        return my_argparser.parse_args()

    def process_args(self):
        args = self.get_args()

        args.fn_inputs = list(map(path.abspath, args.fn_inputs))
        invalid_files = "\n".join(
            filter(lambda f: not path.isfile(f), args.fn_inputs)
        )
        if invalid_files:
            sys.exit(
                "The following files either do not exist or are not regular"
                f" files: \n\n{invalid_files}"
            )

        args.fn_freq_output = path.abspath(args.fn_freq_output)
        args.dir_match_output = path.splitext(args.fn_freq_output)[0]

        if args.dir_parser is None:
            args.dir_parser = os.getenv("STANFORD_PARSER_HOME")
        if args.dir_parser is None:
            sys.exit("Error: Stanford Parser not found.")
        if args.dir_tregex is None:
            args.dir_tregex = os.getenv("STANFORD_TREGEX_HOME")
        if args.dir_tregex is None:
            sys.exit("Error: Tregex not found.")

        # curdir = path.dirname(__file__)
        # if args.dir_parser is None:
        # try:
        #     args.dir_parser = glob.glob(
        #         path.join(curdir, "stanford-parser*", "")
        #     )[0]
        # except IndexError:
        #     sys.exit("Error: Stanford Parser not found under src/.")
        # if args.dir_tregex is None:
        #     try:
        #         args.dir_tregex = glob.glob(
        #             path.join(curdir, "stanford-tregex*", "")
        #         )[0]
        #     except IndexError:
        #         sys.exit('Error: Tregex not found under "src/".')
        return args
