import argparse
import logging
import os.path as os_path
import sys
from typing import Callable, List

from ..scaio import SCAIO
from ..scaprint import color_print, get_yes_or_no
from ..util import SCAProcedureResult
from .lca import LCA


class LCAUI:
    def __init__(self) -> None:
        self.args_parser: argparse.ArgumentParser = self.create_args_parser()
        self.options: argparse.Namespace = argparse.Namespace()

        self.is_spacy_initialized: bool = False

    def create_args_parser(self) -> argparse.ArgumentParser:
        args_parser = argparse.ArgumentParser(
            prog="nsca-lca", formatter_class=argparse.RawDescriptionHelpFormatter
        )
        args_parser.add_argument(
            "--wordlist",
            dest="wordlist",
            choices=("bnc", "anc"),
            default="bnc",
            help=(
                "Choose BNC or ANC (American National Corpus) wordlist for lexical"
                ' sophistication analysis. The default is "bnc".'
            ),
        )
        args_parser.add_argument(
            "--output-file",
            "-o",
            metavar="<filename>",
            dest="ofile",
            default=None,
            help='Specify an output file. The default is "result.csv".',
        )
        args_parser.add_argument(
            "--stdout",
            dest="is_stdout",
            action="store_true",
            default=False,
            help="Write the output to the stdout instead of saving it to a file.",
        )
        return args_parser

    def parse_args(self, argv: List[str]) -> SCAProcedureResult:
        options, ifile_list = self.args_parser.parse_known_args(argv[1:])
        logging.basicConfig(format="%(message)s", level=logging.INFO)

        ofile = options.ofile
        if ofile is not None:
            ofile_ext = os_path.splitext(options.ofile)[-1].lstrip(".")
            if ofile_ext != "csv":
                return (
                    False,
                    f"The file extension {ofile_ext} is not supported. Please use csv.",
                )
        else:
            options.ofile = "result.csv"

        self.verified_ifiles = SCAIO.get_verified_ifile_list(ifile_list)
        self.init_kwargs = {
            "wordlist": options.wordlist,
            "ofile": options.ofile,
            "is_stdout": options.is_stdout,
        }
        self.options = options
        return True, None

    def install_spacy(self) -> SCAProcedureResult:
        import subprocess
        from subprocess import CalledProcessError

        command = [sys.executable, "-m", "pip", "install", "spacy"]
        try:
            subprocess.run(command, check=True, capture_output=False)
        except CalledProcessError as e:
            return False, f"Failed to install spaCy: {e}"

        command = [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
        try:
            subprocess.run(command, check=True, capture_output=False)
        except CalledProcessError as e:
            return False, f"Failed to install spaCy: {e}"

        return True, None

    def check_spacy(self):
        try:
            logging.info("Trying to load spaCy...")
            import spacy  # type: ignore # noqa: F401 'en_core_web_sm' imported but unused
        except ModuleNotFoundError:
            is_install = get_yes_or_no(
                "Running LCA requires spaCy. Do you want me to install it for you?"
            )
            if not is_install:
                return (
                    False,
                    (
                        "\nspaCy installation refused. You need to manually install it using:"
                        "\npip install spacy"
                        "\npython -m spacy download en_core_web_sm"
                    ),
                )
            return self.install_spacy()
        else:
            color_print("OKGREEN", "ok", prefix="spaCy has already been installed. ")
            return True, None

    def run_tmpl(func: Callable):  # type:ignore
        def wrapper(self, *args, **kwargs):
            sucess, err_msg = self.check_spacy()
            if not sucess:
                return sucess, err_msg
            if not self.options.is_stdout:
                sucess, err_msg = SCAIO.is_writable(self.options.ofile)
                if not sucess:
                    return sucess, err_msg
            func(self, *args, **kwargs)
            return True, None

        return wrapper

    @run_tmpl
    def run_on_ifiles(self) -> SCAProcedureResult:
        analyzer = LCA(**self.init_kwargs)
        analyzer.run_on_ifiles(self.verified_ifiles)
        return True, None

    def run(self) -> SCAProcedureResult:
        if self.verified_ifiles:
            return self.run_on_ifiles()
        else:
            self.args_parser.print_help()
            return True, None


def lca_main() -> None:
    ui = LCAUI()
    success, err_msg = ui.parse_args(sys.argv)
    if not success:
        logging.critical(err_msg)
        sys.exit(1)
    success, err_msg = ui.run()
    if not success:
        logging.critical(err_msg)
        sys.exit(1)
