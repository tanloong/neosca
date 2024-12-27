import logging
import os
import os.path as os_path
import re

from neosca.ns_main_cli import Ns_Main_Cli

from .cmdline_tmpl import CmdlineTmpl

cli_text = "This is a test."


class TestCommandLine(CmdlineTmpl):
    def setUp(self):
        self.ui = Ns_Main_Cli()
        super().setUp()

    def test_no_file(self):
        result = self.template(["python", "-m", "neosca"], expected_output_file=None)
        result_stdout = result.stdout.decode("utf8")
        self.assertIn("help", result_stdout)
        #  Check for a few more arguments to ensure we hit the intended argumentParser
        self.assertIn("commands:", result_stdout)
        self.assertIn("sca", result_stdout)
        self.assertIn("lca", result_stdout)
        self.assertIn("gui", result_stdout)

    def test_help(self):
        """Test that all three options print the same help page"""
        result = self.template(["python", "-m", "neosca"], expected_output_file=None)
        result_h = self.template(["python", "-m", "neosca", "-h"], expected_output_file=None)
        result_help = self.template(["python", "-m", "neosca", "--help"], expected_output_file=None)

        self.assertEqual(result_h.stdout.decode("utf-8"), result_help.stdout.decode("utf-8"))
        self.assertEqual(result.stdout.decode("utf-8"), result_h.stdout.decode("utf-8"))

        for subcommand in ("sca", "lca"):
            logging.info(f"Comparing help messages for subcommand {subcommand}...")
            result = self.template(["python", "-m", "neosca", subcommand], expected_output_file=None)
            result_h = self.template(["python", "-m", "neosca", subcommand, "-h"], expected_output_file=None)
            result_help = self.template(
                ["python", "-m", "neosca", subcommand, "--help"], expected_output_file=None
            )

            self.assertEqual(result_h.stdout.decode("utf-8"), result_help.stdout.decode("utf-8"))
            self.assertEqual(result.stdout.decode("utf-8"), result_h.stdout.decode("utf-8"))

    def test_text_input(self):
        for subcommand in ("sca", "lca"):
            args = ["nsca", subcommand, "--text", cli_text]
            self.ui.parse_args(args)
            self.assertEqual(self.ui.options.text, cli_text)
            self.assertFalse(self.ui.options.is_cache)
            self.assertFalse(self.ui.options.is_use_cache)
            self.assertFalse(self.ui.options.is_save_matches)
            self.assertFalse(self.ui.options.is_stdout)
            self.assertEqual(self.ui.options.ofile_freq, f"neosca_{subcommand}_results.csv")
            self.assertEqual(self.ui.options.oformat_freq, "csv")
            self.assertEqual(self.ui.odir_matched, f"neosca_{subcommand}_matches")

            args = [
                "nsca",
                subcommand,
                "--text",
                cli_text,
                "--cache",
                "--use-cache",
                "--save-matches",
                "--stdout",
                "-o",
                "result.json",
            ]
            self.ui.parse_args(args)
            self.assertEqual(self.ui.options.text, cli_text)
            self.assertTrue(self.ui.options.is_cache)
            self.assertTrue(self.ui.options.is_use_cache)
            self.assertTrue(self.ui.options.is_save_matches)
            self.assertTrue(self.ui.options.is_stdout)
            self.assertEqual(self.ui.options.ofile_freq, "result.json")
            self.assertEqual(self.ui.options.oformat_freq, "json")
            self.assertEqual(self.ui.odir_matched, "result_matches")

    def test_no_parse(self):
        args = ["nsca", "sca", "--text", cli_text, "--cache", "--use-cache"]
        self.ui.parse_args(args)
        self.assertFalse(self.ui.options.is_skip_parsing)
        self.assertTrue(self.ui.options.is_cache)
        self.assertTrue(self.ui.options.is_use_cache)

        args = ["nsca", "sca", "--text", cli_text, "--cache", "--use-cache", "--no-parse"]
        self.ui.parse_args(args)
        self.assertTrue(self.ui.options.is_skip_parsing)
        self.assertFalse(self.ui.options.is_cache)
        self.assertFalse(self.ui.options.is_use_cache)

    def test_file_input(self):
        filepaths = list(
            os_path.join(self.testdir_data_txt, file_name)
            for file_name in next(os.walk(self.testdir_data_txt))[2]
        )
        for subcommand in ("sca", "lca"):
            args = ["nsca", subcommand, *filepaths]
            self.ui.parse_args(args)
            self.assertFalse(self.ui.options.is_cache)
            self.assertFalse(self.ui.options.is_use_cache)
            self.assertFalse(self.ui.options.is_save_matches)
            self.assertFalse(self.ui.options.is_stdout)
            self.assertEqual(self.ui.options.ofile_freq, f"neosca_{subcommand}_results.csv")
            self.assertEqual(self.ui.options.oformat_freq, "csv")
            self.assertEqual(self.ui.odir_matched, f"neosca_{subcommand}_matches")

            args = [
                "nsca",
                subcommand,
                *filepaths,
                "--cache",
                "--use-cache",
                "--save-matches",
                "--stdout",
                "-o",
                "result.json",
            ]
            self.ui.parse_args(args)
            self.assertTrue(self.ui.options.is_cache)
            self.assertTrue(self.ui.options.is_use_cache)
            self.assertTrue(self.ui.options.is_save_matches)
            self.assertTrue(self.ui.options.is_stdout)
            self.assertEqual(self.ui.options.ofile_freq, "result.json")
            self.assertEqual(self.ui.options.oformat_freq, "json")
            self.assertEqual(self.ui.odir_matched, "result_matches")

    def test_list_fields(self):
        for subcommand, lineno in (("sca", 23), ("lca", 44)):
            result = self.template(
                ["python", "-m", "neosca", subcommand, "--list"], text=None, expected_output_file=None
            )
            result_stdout = result.stdout.decode("utf-8")
            ncorrect_lines = len(re.findall(r"^[^:]+: [^:]+$", result_stdout, re.MULTILINE))
            self.assertEqual(result_stdout.count("\n"), lineno)
            self.assertEqual(ncorrect_lines, lineno)

    def test_show_version(self):
        result = self.template(["python", "-m", "neosca", "--version"], text=None, expected_output_file=None)
        self.assertRegex(result.stdout.decode("utf-8").strip(), r"[^.]+\.[^.]+\.[^.]+")

    def test_invalid_file(self):
        for subcommand in ("sca", "lca"):
            self.template(
                ["python", "-m", "neosca", subcommand, "no_such_file.txt"],
                success=False,
                expected_output_file=[],
            )
