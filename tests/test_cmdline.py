import os.path as os_path
import re

from .cmdline_tmpl import CmdlineTmpl

cmdline_text = "This is a test."


class TestCommandLineBasic(CmdlineTmpl):
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
                "cmdline_text.pickle.lzma",
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
                "cmdline_text.pickle.lzma",
                "result_matches/cmdline_text/cmdline_text-C1.txt",
                "result_matches/cmdline_text/cmdline_text-S.txt",
                "result_matches/cmdline_text/cmdline_text-T1.txt",
                "result_matches/cmdline_text/cmdline_text-VP1.txt",
            ],
        )

    def test_parse_ifiles(self):
        self.template(
            ["python", "-m", "neosca", "sample.txt", "--no-query"],
            expected_output_file=["sample.pickle.lzma"],
        )
        self.template(
            ["python", "-m", "neosca", self.samples_dir, "--no-query"],
            expected_output_file=[
                os_path.join(self.samples_dir, "sample1.pickle.lzma"),
                os_path.join(self.samples_dir, "sample2.pickle.lzma"),
            ],
        )

    def test_parse_ifiles_and_query(self):
        self.template(
            ["python", "-m", "neosca", "sample.txt", "--reserve-parsed", "--reserve-matched"],
            expected_output_file=[
                "result.csv",
                "sample.pickle.lzma",
                "result_matches/sample/sample-C1.txt",
                "result_matches/sample/sample-S.txt",
                "result_matches/sample/sample-T1.txt",
                "result_matches/sample/sample-VP1.txt",
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
                os_path.join(self.samples_dir, "sample1.pickle.lzma"),
                os_path.join(self.samples_dir, "sample2.pickle.lzma"),
                "result_matches/sample1/sample1-C1.txt",
                "result_matches/sample1/sample1-CN1.txt",
                "result_matches/sample1/sample1-CP.txt",
                "result_matches/sample1/sample1-CT.txt",
                "result_matches/sample1/sample1-DC.txt",
                "result_matches/sample1/sample1-S.txt",
                "result_matches/sample1/sample1-T1.txt",
                "result_matches/sample1/sample1-VP1.txt",
                "result_matches/sample2/sample2-C1.txt",
                "result_matches/sample2/sample2-CN1.txt",
                "result_matches/sample2/sample2-CN2.txt",
                "result_matches/sample2/sample2-CP.txt",
                "result_matches/sample2/sample2-CT.txt",
                "result_matches/sample2/sample2-DC.txt",
                "result_matches/sample2/sample2-S.txt",
                "result_matches/sample2/sample2-T1.txt",
                "result_matches/sample2/sample2-VP1.txt",
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
                os_path.join(self.project_dir, "imgs"),
                "--reserve-parsed",
                "--reserve-matched",
            ],
            expected_output_file=[
                "result.csv",
                os_path.join(self.samples_dir, "sample1.pickle.lzma"),
                os_path.join(self.samples_dir, "sample2.pickle.lzma"),
                "result_matches/sample1/sample1-C1.txt",
                "result_matches/sample1/sample1-CN1.txt",
                "result_matches/sample1/sample1-CP.txt",
                "result_matches/sample1/sample1-CT.txt",
                "result_matches/sample1/sample1-DC.txt",
                "result_matches/sample1/sample1-S.txt",
                "result_matches/sample1/sample1-T1.txt",
                "result_matches/sample1/sample1-VP1.txt",
                "result_matches/sample2/sample2-C1.txt",
                "result_matches/sample2/sample2-CN1.txt",
                "result_matches/sample2/sample2-CN2.txt",
                "result_matches/sample2/sample2-CP.txt",
                "result_matches/sample2/sample2-CT.txt",
                "result_matches/sample2/sample2-DC.txt",
                "result_matches/sample2/sample2-S.txt",
                "result_matches/sample2/sample2-T1.txt",
                "result_matches/sample2/sample2-VP1.txt",
            ],
        )

        # skip .pickle.lzma files
        parsed_file = os_path.join(self.samples_dir, "1.pickle.lzma")
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
            expected_output_file=["result.csv", "sample.pickle.lzma", "result_matches"],
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
                "sample.pickle.lzma",
                "result_matches/sample/sample-C1.txt",
                "result_matches/sample/sample-S.txt",
                "result_matches/sample/sample-T1.txt",
                "result_matches/sample/sample-VP1.txt",
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
                "sample.pickle.lzma",
                "sample_matches/sample/sample-C1.txt",
                "sample_matches/sample/sample-S.txt",
                "sample_matches/sample/sample-T1.txt",
                "sample_matches/sample/sample-VP1.txt",
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
                "sample.pickle.lzma",
                "sample_matches/sample/sample-C1.txt",
                "sample_matches/sample/sample-S.txt",
                "sample_matches/sample/sample-T1.txt",
                "sample_matches/sample/sample-VP1.txt",
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
