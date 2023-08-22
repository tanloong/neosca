import os.path as os_path
import re

from .cmdline_tmpl import CmdlineTmpl

cmdline_text = "This is a test."


class TestCommandLineBasic(CmdlineTmpl):
    def setUp(self):
        self.test_dir = os_path.dirname(os_path.abspath(__file__))
        self.samples_dir = os_path.join(self.test_dir, "data", "samples")
        self.project_dir = os_path.dirname(self.test_dir)
        return super().setUp()

    def test_no_file(self):
        result = self.template(["python", "-m", "neosca"], expected_output_file=None)
        result_stdout = result.stdout.decode("utf8")
        self.assertIn("help", result_stdout)
        #  Check for a few more arguments to ensure we hit the intended argumentParser
        self.assertIn("--text", result_stdout)
        self.assertIn("--output-file", result_stdout)
        self.assertIn("--no-query", result_stdout)

    def test_help(self):
        """Test that all three options print the same help page"""
        result = self.template(["python", "-m", "neosca"], expected_output_file=None)
        result_h = self.template(["python", "-m", "neosca", "-h"], expected_output_file=None)
        result_help = self.template(
            ["python", "-m", "neosca", "--help"], expected_output_file=None
        )

        self.assertEqual(result_h.stdout.decode("utf-8"), result_help.stdout.decode("utf-8"))
        self.assertEqual(result.stdout.decode("utf-8"), result_h.stdout.decode("utf-8"))

    def test_parse_text(self):
        self.template(
            ["python", "-m", "neosca", "--text", f"'{cmdline_text}'", "--no-query"],
            expected_output_file=[
                "cmdline_text.parsed",
            ],
        )

    def test_parse_text_and_query(self):
        self.template(
            [
                "python",
                "-m",
                "neosca",
                "--text",
                f"'{cmdline_text}'",
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=[
                "result.csv",
                "cmdline_text.parsed",
                "result_matches",
            ],
        )

    def test_parse_ifiles(self):
        self.template(
            ["python", "-m", "neosca", "sample.txt", "--no-query"],
            expected_output_file=["sample.parsed"],
        )
        self.template(
            ["python", "-m", "neosca", self.samples_dir, "--no-query"],
            expected_output_file=[
                os_path.join(self.samples_dir, "sample1.parsed"),
                os_path.join(self.samples_dir, "sample2.parsed"),
            ],
        )

    def test_parse_ifiles_and_query(self):
        self.template(
            ["python", "-m", "neosca", "sample.txt", "--reserve-parsed", "--reserve-matched"],
            expected_output_file=[
                "result.csv",
                "sample.parsed",
                "result_matches",
            ],
        )
        self.template(
            [
                "python",
                "-m",
                "neosca",
                self.samples_dir,
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=[
                "result.csv",
                os_path.join(self.samples_dir, "sample1.parsed"),
                os_path.join(self.samples_dir, "sample2.parsed"),
                "result_matches",
            ],
        )

    def test_skip_files(self):
        # skip files of unsupported type
        self.template(
            [
                "python",
                "-m",
                "neosca",
                self.samples_dir,
                # gif file
                os_path.join(self.project_dir, "img"),
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=[
                "result.csv",
                os_path.join(self.samples_dir, "sample1.parsed"),
                os_path.join(self.samples_dir, "sample2.parsed"),
                "result_matches",
            ],
        )

        # skip .parsed files
        parsed_file = os_path.join(self.samples_dir, "1.parsed")
        open(parsed_file, "a").close()
        self.template(
            ["python", "-m", "neosca", self.samples_dir], expected_output_file=["result.csv"]
        )
        self.cleanup(parsed_file)

    def test_outputfile(self):
        self.template(
            [
                "python",
                "-m",
                "neosca",
                "sample.txt",
                "--output-format",
                "csv",
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=["result.csv", "sample.parsed", "result_matches"],
        )
        self.template(
            [
                "python",
                "-m",
                "neosca",
                "sample.txt",
                "--output-format",
                "json",
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=[
                "result.json",
                "sample.parsed",
                "result_matches",
            ],
        )
        self.template(
            [
                "python",
                "-m",
                "neosca",
                "sample.txt",
                "--output-file",
                "sample.csv",
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=[
                "sample.csv",
                "sample.parsed",
                "sample_matches",
            ],
        )
        self.template(
            [
                "python",
                "-m",
                "neosca",
                "sample.txt",
                "--output-file",
                "sample.json",
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=[
                "sample.json",
                "sample.parsed",
                "sample_matches",
            ],
        )

    def test_list_fields(self):
        result = self.template(
            ["python", "-m", "neosca", "--list"], text=None, expected_output_file=None
        )
        result_stdout = result.stdout.decode("utf-8")
        ncorrect_lines = len(re.findall(r"^[A-Z/]+: .*$", result_stdout, re.MULTILINE))
        self.assertEqual(result_stdout.count("\n"), 23)
        self.assertEqual(ncorrect_lines, 23)

    def test_show_version(self):
        result = self.template(
            ["python", "-m", "neosca", "--version"], text=None, expected_output_file=None
        )
        self.assertRegex(result.stdout.decode("utf-8").strip(), r"[^.]+\.[^.]+\.[^.]+")

    def test_invalid_file(self):
        self.template(
            ["python", "-m", "neosca", "no_such_file.txt"],
            success=False,
            expected_output_file=[],
        )
