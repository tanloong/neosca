import argparse
import glob
import logging
import os
import os.path as os_path
import sys
from typing import Callable, List, Optional

from neosca.ns_about import __title__, __version__
from neosca.ns_io import Ns_Cache, Ns_IO
from neosca.ns_print import color_print
from neosca.ns_util import Ns_Procedure_Result


class Ns_Main_Cli:
    def __init__(self) -> None:
        self.cwd = os.getcwd()
        self.args_parser: argparse.ArgumentParser = self.create_args_parser()
        self.options: argparse.Namespace = argparse.Namespace()

    def create_args_parser(self) -> argparse.ArgumentParser:
        args_parser = argparse.ArgumentParser(prog="nsca", formatter_class=argparse.RawDescriptionHelpFormatter)
        args_parser.add_argument(
            "--version",
            action="store_true",
            default=False,
            help="Show version and exit.",
        )
        args_parser.add_argument(
            "--gui",
            action="store_true",
            default=False,
            help="Start the program with a graphical user interface.",
        )
        args_parser.add_argument(
            "--list",
            dest="list_fields",
            action="store_true",
            default=False,
            help="List built-in measures.",
        )
        args_parser.add_argument(
            "--expand-wildcards",
            dest="expand_wildcards",
            action="store_true",
            default=False,
            help=(
                "Print all files that match your wildcard pattern. This can help you ensure that"
                " your pattern matches all desired files and excludes any unwanted ones. Note"
                " that files that do not exist on the computer will not be included in the"
                " output, even if they match the specified pattern."
            ),
        )
        args_parser.add_argument(
            "--combine-files",
            "-c",
            metavar="<subfile>",
            dest="subfiles_list",
            action="append",
            default=None,
            nargs="+",
            help="Combine frequency output of multiple files.",
        )
        args_parser.add_argument(
            "--text",
            "-t",
            metavar="<text>",
            default=None,
            help="Pass text through the command line.",
        )
        args_parser.add_argument(
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
        args_parser.add_argument(
            "--output-file",
            "-o",
            metavar="<filename>",
            dest="ofile_freq",
            default=None,
            help='Specify an output file. The default is "result.csv".',
        )
        args_parser.add_argument(
            "--output-format",
            dest="oformat_freq",
            choices=["csv", "json"],
            default="csv",
            help='Output format, the default is "csv".',
        )
        args_parser.add_argument(
            "--stdout",
            dest="is_stdout",
            action="store_true",
            default=False,
            help="Write the frequency output to the stdout instead of saving it to a file.",
        )
        args_parser.add_argument(
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
        args_parser.add_argument(
            "--cache",
            dest="is_cache",
            action="store_true",
            default=False,
            help="Cache uncached files for faster future runs.",
        )
        args_parser.add_argument(
            "--use-cache",
            dest="is_use_cache",
            action="store_true",
            default=False,
            help="Use cache if available.",
        )
        args_parser.add_argument(
            "--save-matches",
            "-m",
            dest="is_save_matches",
            default=False,
            action="store_true",
            help="Save the matched subtrees.",
        )
        args_parser.add_argument(
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
        args_parser.add_argument(
            "--quiet",
            dest="is_quiet",
            action="store_true",
            default=False,
            help=f"Stop {__title__} from printing anything except for final results.",
        )
        args_parser.add_argument(
            "--verbose",
            dest="is_verbose",
            action="store_true",
            default=False,
            help="Print detailed logging messages.",
        )
        # args_parser.add_argument(
        #     "--yes",
        #     dest="is_assume_yes",
        #     action="store_true",
        #     default=False,
        #     help="Assume the answer to all prompts is yes, used when installing dependencies.",
        # )
        # args_parser.add_argument(
        #     "--config",
        #     dest="config",
        #     default=None,
        #     help=(
        #         "Use custom json file where you can define your own syntactic structures to"
        #         " search or calculate."
        #     ),
        # )
        return args_parser

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

        if options.is_skip_parsing:
            options.is_cache = False
            options.is_use_cache = False

        if options.text is not None:
            if ifile_list:
                return False, "Unexpected argument(s):\n\n{}".format("\n".join(ifile_list))
            logging.info(f"CLI text: {options.text}")
            self.verified_ifiles = None
        else:
            self.verified_ifiles = Ns_IO.get_verified_ifile_list(ifile_list)

        if options.subfiles_list is None:
            self.verified_subfiles_list: List[List[str]] = []
        else:
            verified_subfiles_list = []
            for subfiles in options.subfiles_list:
                verified_subfiles = []
                for path in subfiles:
                    if os_path.isfile(path):
                        verified_subfiles.append(path)
                    elif os_path.isdir(path):
                        for ftype in options.ifile_types:
                            verified_subfiles.extend(glob.glob(f"{path}{os_path.sep}*.{ftype}"))
                    elif glob.glob(path):
                        verified_subfiles.extend(glob.glob(path))
                    else:
                        return False, f"No such file as\n\n{path}"
                if len(verified_subfiles) == 1:
                    logging.critical(
                        f"Only 1 subfile provided: ({verified_subfiles[0]}). There should be 2"
                        " or more subfiles to combine."
                    )
                    sys.exit(1)
                verified_subfiles_list.append(verified_subfiles)
            self.verified_subfiles_list = verified_subfiles_list

        self.odir_matched = "result_matches"
        if options.ofile_freq is not None:
            self.odir_matched = os_path.splitext(options.ofile_freq)[0] + "_matches"
            ofile_freq_ext = os_path.splitext(options.ofile_freq)[-1].lstrip(".")
            if ofile_freq_ext not in ("csv", "json"):
                return (
                    False,
                    (
                        f"The file extension {ofile_freq_ext} is not supported. Use one of"
                        " the following:\n1. csv\n2. json"
                    ),
                )
            if ofile_freq_ext != options.oformat_freq:
                options.oformat_freq = ofile_freq_ext
        else:
            options.ofile_freq = "result." + options.oformat_freq

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
            logging.debug(f"[Main] Using configuration file {user_config}")
        else:
            default_config_file = "nsca.json"
            if os_path.isfile(default_config_file):
                user_config = default_config_file
                logging.debug(f"[Main] Using configuration file {user_config}")
            else:
                logging.debug("[Main] No configuration file found")

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
        self.options = options
        return True, None

    def check_python(self) -> Ns_Procedure_Result:
        v_info = sys.version_info
        if v_info.minor >= 8 and v_info.major == 3:
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
        if self.options.is_cache:
            if self.verified_ifiles or self.verified_subfiles_list:
                msg_num += 1
                logging.info(
                    f"{msg_num}. parse trees were saved corresponding to input files,"
                    ' with the same name but a ".parsed" extension.'
                )
            elif self.options.text is not None:
                msg_num += 1
                color_print(
                    "OKGREEN",
                    f"{self.cwd}{os.sep}cli_text.parsed",
                    prefix=f"{msg_num}. parse trees were saved to ",
                    postfix=".",
                )
        if self.options.is_save_matches:
            msg_num += 1
            color_print(
                "OKGREEN",
                f"{os_path.abspath(self.odir_matched)}",
                prefix=f"{msg_num}. Matched subtrees were saved to ",
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
    def run_on_text(self) -> None:
        from neosca.ns_sca.ns_sca import Ns_SCA

        analyzer = Ns_SCA(**self.init_kwargs)
        analyzer.run_on_text(self.options.text)

    @run_tmpl
    def run_on_ifiles(self) -> None:
        from neosca.ns_sca.ns_sca import Ns_SCA

        analyzer = Ns_SCA(**self.init_kwargs)

        files = []
        if self.verified_ifiles:
            files.extend(self.verified_ifiles)
        if self.verified_subfiles_list:
            files.extend(self.verified_subfiles_list)
        analyzer.run_on_file_or_subfiles_list(files)

    def run_gui(self) -> Ns_Procedure_Result:
        from neosca.ns_main_gui import main_gui

        main_gui()
        return True, None

    def run(self) -> Ns_Procedure_Result:
        if self.options.version:
            return self.show_version()
        elif self.options.gui:
            return self.run_gui()
        elif self.options.list_fields:
            return self.list_fields()
        elif self.options.expand_wildcards:
            return self.expand_wildcards()
        elif self.options.text is not None:
            return self.run_on_text()  # type: ignore
        elif self.verified_ifiles or self.verified_subfiles_list:
            return self.run_on_ifiles()  # type: ignore
        else:
            self.args_parser.print_help()
            return True, None

    def list_fields(self) -> Ns_Procedure_Result:
        from neosca.ns_sca.structure_counter import StructureCounter

        counter = StructureCounter()
        for s_name in counter.selected_measures:
            print(f"{s_name}: {counter.get_structure(s_name).description}")
        return True, None

    def expand_wildcards(self) -> Ns_Procedure_Result:
        is_not_found = True
        if self.verified_ifiles:
            is_not_found = False
            print("Input files:")
            for i, ifile in enumerate(self.verified_ifiles, 1):
                print(f" {i}. {ifile}")
        if self.verified_subfiles_list:
            is_not_found = False
            for i, subfiles in enumerate(self.verified_subfiles_list, 1):
                print(f"Input subfile list {i}:")
                for j, subfile in enumerate(subfiles, 1):
                    print(f" {j}. {subfile}")
        if is_not_found:
            print("0 files and subfiles are found.")
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
