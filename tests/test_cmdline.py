import re
from .cmdline_tmpl import CmdlineTmpl

cmdline_text = "This is a test."

class TestCommandLineBasic(CmdlineTmpl):
    def test_no_file(self):
        result = self.template("python -m neosca", expected_output_file=None)
        result_stdout = result.stdout.decode("utf8")
        self.assertIn("help", result_stdout)
        #  Check for a few more arguments to ensure we hit the intended argumentParser
        self.assertIn("--parser", result_stdout)
        self.assertIn("--tregex", result_stdout)
        self.assertIn("--output-file", result_stdout)

    def test_help(self):
        """Test that all three options print the same help page"""
        result = self.template("python -m neosca", expected_output_file=None)
        result_h = self.template(
            "python -m neosca -h", expected_output_file=None
        )
        result_help = self.template(
            "python -m neosca --help", expected_output_file=None
        )

        self.assertEqual(
            result_h.stdout.decode("utf-8"), result_help.stdout.decode("utf-8")
        )
        self.assertEqual(
            result.stdout.decode("utf-8"), result_h.stdout.decode("utf-8")
        )

    def test_parse_text(self):
        self.template(
            f"python -m neosca --text '{cmdline_text}' --no-query",
            expected_output_file=[
                "cmdline_text.parsed",
            ],
        )

    def test_parse_text_and_query(self):
        self.template(
            f"python -m neosca --text '{cmdline_text}' --reserve-parsed"
            " --reserve-matched",
            expected_output_file=[
                "result.csv",
                "cmdline_text.parsed",
                "result_matches",
            ],
        )

    def test_parse_ifiles(self):
        self.template(
            "python -m neosca sample.txt --no-query",
            expected_output_file=[
                "sample.parsed",
            ],
        )

    def test_parse_ifiles_and_query(self):
        self.template(
            "python -m neosca sample.txt --reserve-parsed --reserve-matched",
            expected_output_file=[
                "result.csv",
                "sample.parsed",
                "result_matches",
            ],
        )

    def test_outputfile(self):
        self.template(
            "python -m neosca sample.txt --output-file result.csv --reserve-parsed"
            " --reserve-matched",
            expected_output_file=[
                "result.csv",
                "sample.parsed",
                "result_matches",
            ],
        )

    def test_show_version(self):
        result = self.template(
            "python -m neosca --version", text=None, expected_output_file=None
        )
        m = re.match(
            r"[^.]*\.[^.]*\.[^.]*", result.stdout.decode("utf-8").strip()
        )
        self.assertNotEqual(m, None)

    def test_invalid_file(self):
        self.template(
            "python -m neosca no_such_file.txt",
            success=False,
            expected_output_file=[],
        )
