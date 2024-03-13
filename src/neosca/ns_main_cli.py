import argparse
import logging
import os
import os.path as os_path
import sys
from typing import Callable, List, Optional

from neosca import CACHE_DIR
from neosca.ns_about import __title__, __version__
from neosca.ns_io import Ns_Cache, Ns_IO
from neosca.ns_lca.ns_lca import Ns_LCA
from neosca.ns_print import color_print
from neosca.ns_sca.ns_sca import Ns_SCA
from neosca.ns_utils import Ns_Procedure_Result


class Ns_Main_Cli:
    def __init__(self) -> None:
        self.cwd = os.getcwd()
        self.args_parser: argparse.ArgumentParser = self.create_args_parser()
        self.options: argparse.Namespace = argparse.Namespace()

    def __add_log_levels(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--quiet",
            dest="is_quiet",
            action="store_true",
            default=False,
            help="disable all logging",
        )
        parser.add_argument(
            "--verbose",
            dest="is_verbose",
            action="store_true",
            default=False,
            help="enable verbose logging",
        )

    def create_args_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="nsca", formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument(
            "--version",
            action="store_true",
            default=False,
            help="show version and exit",
        )
        self.__add_log_levels(parser)
        subparsers: argparse._SubParsersAction = parser.add_subparsers(title="commands", dest="command")
        self.sca_parser = self.create_sca_parser(subparsers)
        self.lca_parser = self.create_lca_parser(subparsers)
        self.gui_parser = self.create_gui_parser(subparsers)
        return parser

    def create_sca_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        sca_parser = subparsers.add_parser("sca", help="syntactic complexity analyzer")

        sca_parser.add_argument(
            "--list",
            dest="list_fields",
            action="store_true",
            default=False,
            help="List built-in measures.",
        )
        sca_parser.add_argument(
            "--combine-files",
            "-c",
            metavar="<subfile>",
            dest="subfiles_list",
            action="append",
            default=None,
            nargs="+",
            help="Combine frequency output of multiple files.",
        )
        sca_parser.add_argument(
            "--text",
            "-t",
            metavar="<text>",
            default=None,
            help="Pass text through the command line.",
        )
        sca_parser.add_argument(
            "--ftype",
            dest="ifile_types",
            choices=Ns_IO.SUPPORTED_EXTENSIONS,
            default=Ns_IO.SUPPORTED_EXTENSIONS,
            nargs="+",
            help=(
                "Analyze files of the specified type(s). If not set, the program will process"
                " files of all supported types."
            ),
        )
        sca_parser.add_argument(
            "--output-file",
            "-o",
            metavar="<filename>",
            dest="ofile_freq",
            default=None,
            help='Specify an output file. The default is "result.csv".',
        )
        sca_parser.add_argument(
            "--output-format",
            dest="oformat_freq",
            choices=["csv", "json"],
            default="csv",
            help='Output format, the default is "csv".',
        )
        sca_parser.add_argument(
            "--stdout",
            dest="is_stdout",
            action="store_true",
            default=False,
            help="Write the frequency output to the stdout instead of saving it to a file.",
        )
        sca_parser.add_argument(
            "--select",
            metavar="<measure>",
            dest="selected_measures",
            default=None,
            nargs="+",
            help=(
                "Select only some of the measures to analyze. The builtin measures include"
                ' "W", "S", "VP", "C", "T", "DC", "CT", "CP", "CN", "MLS", "MLT", "MLC", "C/S",'
                ' "VP/T", "C/T", "DC/C", "DC/T", "T/S", "CT/T", "CP/T", "CP/C", "CN/T", and'
                ' "CN/C".'
            ),
        )
        sca_parser.add_argument(
            "--cache",
            dest="is_cache",
            action="store_true",
            default=False,
            help="Cache uncached files for faster future runs.",
        )
        sca_parser.add_argument(
            "--use-cache",
            dest="is_use_cache",
            action="store_true",
            default=False,
            help="Use cache if available.",
        )
        sca_parser.add_argument(
            "--save-matches",
            "-m",
            dest="is_save_matches",
            default=False,
            action="store_true",
            help="Save the matched subtrees.",
        )
        sca_parser.add_argument(
            "--no-parse",
            dest="is_skip_parsing",
            action="store_true",
            default=False,
            help=(
                "Assume input as parse trees. By default, the program expects"
                " raw text as input that will be parsed before querying. If you"
                " already have parsed input files, use this flag to indicate that"
                " the program should skip the parsing step and proceed directly"
                " to querying. When this flag is set, the --cache and --use-cache"
                " flags will be automatically set as False."
            ),
        )
        # parser_sca.add_argument(
        #     "--config",
        #     dest="config",
        #     default=None,
        #     help=(
        #         "Use custom json file where you can define your own syntactic structures to"
        #         " search or calculate."
        #     ),
        # )
        self.__add_log_levels(sca_parser)
        sca_parser.set_defaults(func=self.parse_sca_args, analyzer_class=Ns_SCA)
        return sca_parser

    def create_lca_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        lca_parser: argparse.ArgumentParser = subparsers.add_parser("lca", help="lexical complexity analyzer")
        lca_parser.add_argument(
            "--list",
            dest="list_fields",
            action="store_true",
            default=False,
            help="List built-in measures.",
        )
        lca_parser.add_argument(
            "--combine-files",
            "-c",
            metavar="<subfile>",
            dest="subfiles_list",
            action="append",
            default=None,
            nargs="+",
            help="Combine frequency output of multiple files.",
        )
        lca_parser.add_argument(
            "--wordlist",
            dest="wordlist",
            choices=("bnc", "anc"),
            default="bnc",
            help=(
                "Choose BNC or ANC (American National Corpus) wordlist for lexical"
                ' sophistication analysis. The default is "bnc".'
            ),
        )
        lca_parser.add_argument(
            "--tagset",
            dest="tagset",
            choices=("ud", "ptb"),
            default="ud",
            help='Choose UD or PTB POS tagset for word classification. The default is "ud".',
        )
        lca_parser.add_argument(
            "--output-file",
            "-o",
            metavar="<filename>",
            dest="ofile_freq",
            default=None,
            help='Specify an output file. The default is "result.csv".',
        )
        lca_parser.add_argument(
            "--output-format",
            dest="oformat_freq",
            choices=["csv", "json"],
            default="csv",
            help='Output format, the default is "csv".',
        )
        lca_parser.add_argument(
            "--stdout",
            dest="is_stdout",
            action="store_true",
            default=False,
            help="Write the output to the stdout instead of saving it to a file.",
        )
        lca_parser.add_argument(
            "--text",
            "-t",
            metavar="<text>",
            default=None,
            help="Pass text through the command line.",
        )
        lca_parser.add_argument(
            "--cache",
            dest="is_cache",
            action="store_true",
            default=False,
            help="Cache uncached files for faster future runs.",
        )
        lca_parser.add_argument(
            "--use-cache",
            dest="is_use_cache",
            action="store_true",
            default=False,
            help="Use cache if available.",
        )
        lca_parser.add_argument(
            "--save-matches",
            "-m",
            dest="is_save_matches",
            default=False,
            action="store_true",
            help="Save the matched words.",
        )
        self.__add_log_levels(lca_parser)
        lca_parser.set_defaults(func=self.parse_lca_args, analyzer_class=Ns_LCA)
        return lca_parser

    def create_gui_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        gui_parser = subparsers.add_parser("gui", help="start the program with GUI")
        self.__add_log_levels(gui_parser)
        gui_parser.set_defaults(is_gui=True)
        return gui_parser

    def parse_sca_args(self, options: argparse.Namespace) -> Ns_Procedure_Result:
        if options.is_skip_parsing:
            options.is_cache = False
            options.is_use_cache = False

        if options.text is not None:
            logging.debug(f"CLI text: {options.text}")

        if options.subfiles_list is None:
            self.verified_subfiles_list: List[List[str]] = []
        else:
            self.verified_subfiles_list = Ns_IO.get_verified_subfiles_list(options.subfiles_list)

        self.odir_matched = "neosca_sca_matches"
        if options.ofile_freq is not None:
            self.odir_matched = os_path.splitext(options.ofile_freq)[0] + "_matches"
            ofile_freq_ext = Ns_IO.suffix(options.ofile_freq, strip_dot=True)
            if ofile_freq_ext not in ("csv", "json"):
                return (
                    False,
                    f"The file extension {ofile_freq_ext} is not supported. Use one of the following:\n1. csv\n2. json",
                )
            if ofile_freq_ext != options.oformat_freq:
                logging.debug(
                    f"Conflict between ofile_freq ({options.ofile_freq}) and oformat_freq ({options.oformat_freq}), using {ofile_freq_ext}"
                )
                options.oformat_freq = ofile_freq_ext
        else:
            options.ofile_freq = f"neosca_sca_results.{options.oformat_freq}"

        if options.selected_measures is not None:
            # Drop duplicates while retain order. Starting from Python 3.7, the
            # built-in dictionary is guaranteed to maintain the insertion order
            options.selected_measures = list(dict.fromkeys(options.selected_measures))

        # user_config = options.config
        user_config = None
        if user_config is not None:
            if not os_path.isfile(user_config):
                return False, f"no such file as\n\n{user_config}"
            if not user_config.endswith(".json"):
                return False, f'"{user_config}" does not seem like a json file.'
            logging.debug(f"Using configuration file {user_config}")
        else:
            default_config_file = "nsca.json"
            if os_path.isfile(default_config_file):
                user_config = default_config_file
                logging.debug(f"Using configuration file {user_config}")
            else:
                logging.debug("No configuration file found")

        self.init_kwargs = {
            "ofile_freq": options.ofile_freq,
            "oformat_freq": options.oformat_freq,
            "odir_matched": self.odir_matched,
            "selected_measures": options.selected_measures,
            "is_cache": options.is_cache,
            "is_use_cache": options.is_use_cache,
            "is_save_matches": options.is_save_matches,
            "is_stdout": options.is_stdout,
            "is_skip_parsing": options.is_skip_parsing,
            "config": user_config,
        }
        return True, None

    def parse_lca_args(self, options: argparse.Namespace) -> Ns_Procedure_Result:
        self.odir_matched = "neosca_lca_matches"
        if options.ofile_freq is not None:
            self.odir_matched = os_path.splitext(options.ofile_freq)[0] + "_matches"
            ofile_freq_ext = Ns_IO.suffix(options.ofile_freq, strip_dot=True)
            if ofile_freq_ext not in ("csv", "json"):
                return (
                    False,
                    f"The file extension {ofile_freq_ext} is not supported. Use one of the following:\n1. csv\n2. json",
                )
            if ofile_freq_ext != options.oformat_freq:
                logging.debug(
                    f"Conflict between ofile_freq ({options.ofile_freq}) and oformat_freq ({options.oformat_freq}), using {ofile_freq_ext}"
                )
                options.oformat_freq = ofile_freq_ext
        else:
            options.ofile_freq = f"neosca_lca_results.{options.oformat_freq}"

        if options.text is not None:
            logging.debug(f"CLI text: {options.text}")

        if options.subfiles_list is None:
            self.verified_subfiles_list: List[List[str]] = []
        else:
            self.verified_subfiles_list = Ns_IO.get_verified_subfiles_list(options.subfiles_list)

        self.init_kwargs = {
            "wordlist": options.wordlist,
            "tagset": options.tagset,
            "ofile_freq": options.ofile_freq,
            "oformat_freq": options.oformat_freq,
            "odir_matched": self.odir_matched,
            "is_stdout": options.is_stdout,
            "is_cache": options.is_cache,
            "is_use_cache": options.is_use_cache,
            "is_save_matches": options.is_save_matches,
        }
        self.options = options
        return True, None

    def parse_args(self, argv: List[str]) -> Ns_Procedure_Result:
        idx: Optional[int] = None
        if "--" in argv[1:]:
            idx = argv.index("--")
        if idx is not None:
            options, ifile_list = self.args_parser.parse_args(argv[1:idx]), argv[idx + 1 :]
        else:
            options, ifile_list = self.args_parser.parse_known_args(argv[1:])

        assert not (
            options.is_quiet and options.is_verbose
        ), "logging cannot be quiet and verbose at the same time"
        if options.is_quiet:
            logging.basicConfig(format="%(message)s", level=logging.CRITICAL)
        elif options.is_verbose:
            logging.basicConfig(format="%(message)s", level=logging.DEBUG)
        else:
            logging.basicConfig(format="%(message)s", level=logging.INFO)

        self.verified_ifiles = Ns_IO.get_verified_ifile_list(ifile_list)

        if (func := getattr(options, "func", None)) is not None:
            func(options)

        self.options = options
        return True, None

    def check_python(self) -> Ns_Procedure_Result:
        v_info = sys.version_info
        if v_info.minor >= 10 and v_info.major == 3:
            return True, None
        else:
            return (
                False,
                (
                    f"Error: Python {v_info.major}.{v_info.minor} is too old."
                    f" {__title__} only supports Python 3.8 or higher."
                ),
            )

    def exit_routine(self) -> None:
        Ns_Cache.save_cache_info()

        if self.options.is_quiet or self.options.is_stdout:
            return

        msg_num = 1
        color_print(
            "OKGREEN",
            f"{os_path.abspath(self.options.ofile_freq)}",
            prefix=f"{msg_num}. Frequency output was saved to ",
            postfix=".",
        )
        if self.options.is_cache and (self.verified_ifiles or self.verified_subfiles_list):
            msg_num += 1
            color_print("OKGREEN", str(CACHE_DIR), prefix=f"{msg_num}. Cache was saved to ", postfix=".")
        if self.options.is_save_matches:
            msg_num += 1
            color_print(
                "OKGREEN",
                f"{os_path.abspath(self.odir_matched)}",
                prefix=f"{msg_num}. Matches were saved to ",
                postfix=".",
            )
        if msg_num > 0:
            logging.info("Done.")

    def run_tmpl(func: Callable):  # type:ignore
        def wrapper(self, *args, **kwargs):
            sucess, err_msg = self.check_python()
            if not sucess:
                return sucess, err_msg
            if not self.options.is_stdout:
                sucess, err_msg = Ns_IO.is_writable(self.options.ofile_freq)
                if not sucess:
                    return sucess, err_msg
            func(self, *args, **kwargs)
            self.exit_routine()
            return True, None

        return wrapper

    @run_tmpl
    def run_on_input(self) -> Ns_Procedure_Result:
        analyzer = self.options.analyzer_class(**self.init_kwargs)

        if self.options.text is not None:
            analyzer.run_on_text(self.options.text)

        files = []
        if verified_ifiles := getattr(self, "verified_ifiles", []):
            files.extend(verified_ifiles)
        if verified_subfiles_list := getattr(self, "verified_subfiles_list", []):
            files.extend(verified_subfiles_list)
        if files:
            analyzer.run_on_file_or_subfiles_list(files)

        return True, None

    def run_gui(self) -> Ns_Procedure_Result:
        from neosca.ns_main_gui import main_gui

        main_gui()
        return True, None

    def run(self) -> Ns_Procedure_Result:
        if self.options.version:
            return self.show_version()
        elif getattr(self.options, "is_gui", False):
            return self.run_gui()
        elif getattr(self.options, "list_fields", False):
            return self.options.analyzer_class.list_fields()
        elif (
            getattr(self, "verified_ifiles", False)
            or getattr(self, "verified_subfiles_list", False)
            or getattr(self.options, "text", None) is not None
        ):
            return self.run_on_input()
        else:
            if (sub_parser := getattr(self, f"{self.options.command}_parser", None)) is not None:
                sub_parser.print_help()
            else:
                self.args_parser.print_help()
            return True, None

    def show_version(self) -> Ns_Procedure_Result:
        print(__version__)
        return True, None


def main_cli() -> None:
    ui = Ns_Main_Cli()
    success, err_msg = ui.parse_args(sys.argv)
    if not success:
        logging.critical(err_msg)
        sys.exit(1)
    success, err_msg = ui.run()
    if not success:
        logging.critical(err_msg)
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
