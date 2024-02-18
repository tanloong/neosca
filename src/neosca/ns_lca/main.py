import argparse
import logging
import os.path as os_path
import sys
from typing import Callable, List

from neosca.ns_io import Ns_IO
from neosca.ns_lca.ns_lca import Ns_LCA
from neosca.ns_print import color_print
from neosca.ns_utils import Ns_Procedure_Result


class LCAUI:
    def __init__(self) -> None:
        self.args_parser: argparse.ArgumentParser = self.create_args_parser()
        self.options: argparse.Namespace = argparse.Namespace()

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
            "--tagset",
            dest="tagset",
            choices=("ud", "ptb"),
            default="ud",
            help='Choose UD or PTB POS tagset for word classification. The default is "ud".',
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
        args_parser.add_argument(
            "--text",
            "-t",
            metavar="<text>",
            default=None,
            help="Pass text through the command line.",
        )
        args_parser.add_argument(
            "--quiet",
            dest="is_quiet",
            action="store_true",
            default=False,
            help="Stop the program from printing anything except for final results.",
        )
        args_parser.add_argument(
            "--verbose",
            dest="is_verbose",
            action="store_true",
            default=False,
            help="Print detailed logging messages.",
        )
        return args_parser

    def parse_args(self, argv: List[str]) -> Ns_Procedure_Result:
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

        if options.text is not None:
            logging.info(f"CLI text: {options.text}")
            if ifile_list:
                return False, "Unexpected argument(s):\n\n{}".format("\n".join(ifile_list))
            self.verified_ifiles = None
        else:
            self.verified_ifiles = Ns_IO.get_verified_ifile_list(ifile_list)

        self.init_kwargs = {
            "wordlist": options.wordlist,
            "tagset": options.tagset,
            "ofile": options.ofile,
            "is_stdout": options.is_stdout,
        }
        self.options = options
        return True, None

    def exit_routine(self) -> None:
        if self.options.is_quiet or self.options.is_stdout:
            return

        color_print(
            "OKGREEN",
            f"{os_path.abspath(self.options.ofile)}",
            prefix="Output has been saved to ",
            postfix=". Done.",
        )

    def run_tmpl(func: Callable):  # type:ignore
        def wrapper(self, *args, **kwargs):
            if not self.options.is_stdout:
                sucess, err_msg = Ns_IO.is_writable(self.options.ofile)
                if not sucess:
                    return sucess, err_msg
            func(self, *args, **kwargs)
            self.exit_routine()
            return True, None

        return wrapper

    @run_tmpl
    def run_on_text(self) -> Ns_Procedure_Result:
        analyzer = Ns_LCA(**self.init_kwargs)
        analyzer.analyze(text=self.options.text)
        return True, None

    @run_tmpl
    def run_on_ifiles(self) -> Ns_Procedure_Result:
        analyzer = Ns_LCA(**self.init_kwargs)
        analyzer.analyze(ifiles=self.verified_ifiles)
        return True, None

    def run(self) -> Ns_Procedure_Result:
        if self.options.text is not None:
            return self.run_on_text()
        elif self.verified_ifiles:
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
