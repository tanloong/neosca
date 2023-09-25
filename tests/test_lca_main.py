import glob
import os.path as os_path

from neosca.lca.main import LCAUI

from .base_tmpl import BaseTmpl

cmdline_text = "This is a test."


class TestLCAMain(BaseTmpl):
    def setUp(self):
        self.ui = LCAUI()
        return super().setUp()

    def test_parse_args(self):
        ui = self.ui
        filepath = os_path.join(self.samples_dir, "sample1.txt")

        # default
        args = ["nsca-lca", filepath]
        ui.parse_args(args)
        self.assertEqual(
            ui.init_kwargs,
            {"wordlist": "bnc", "tagset": "ud", "ofile": "result.csv", "is_stdout": False},
        )
        self.assertIsNone(ui.options.text)
        self.assertIsInstance(ui.verified_ifiles, list)
        self.assertFalse(ui.options.is_verbose)
        self.assertFalse(ui.options.is_quiet)

        args = ["nsca-lca", filepath, "--output-file", "output.csv"]
        ui.parse_args(args)
        self.assertEqual(
            ui.init_kwargs,
            {"wordlist": "bnc", "tagset": "ud", "ofile": "output.csv", "is_stdout": False},
        )
        self.assertIsNone(ui.options.text)
        self.assertIsInstance(ui.verified_ifiles, list)
        self.assertFalse(ui.options.is_verbose)
        self.assertFalse(ui.options.is_quiet)

        args = ["nsca-lca", filepath, "-o", "output.csv"]
        ui.parse_args(args)
        self.assertEqual(
            ui.init_kwargs,
            {"wordlist": "bnc", "tagset": "ud", "ofile": "output.csv", "is_stdout": False},
        )
        self.assertIsNone(ui.options.text)
        self.assertIsInstance(ui.verified_ifiles, list)
        self.assertFalse(ui.options.is_verbose)
        self.assertFalse(ui.options.is_quiet)

        args = ["nsca-lca", filepath, "--stdout"]
        ui.parse_args(args)
        self.assertTrue(ui.options.is_stdout)

        args = ["nsca-lca", "--text", "He came across the road."]
        ui.parse_args(args)
        self.assertEqual(
            ui.init_kwargs,
            {"wordlist": "bnc", "tagset": "ud", "ofile": "result.csv", "is_stdout": False},
        )
        self.assertIsNotNone(ui.options.text)
        self.assertIsNone(ui.verified_ifiles)
        self.assertFalse(ui.options.is_verbose)
        self.assertFalse(ui.options.is_quiet)

        args = ["nsca-lca", "-t", "He came across the road."]
        ui.parse_args(args)
        self.assertEqual(
            ui.init_kwargs,
            {"wordlist": "bnc", "tagset": "ud", "ofile": "result.csv", "is_stdout": False},
        )
        self.assertIsNotNone(ui.options.text)
        self.assertIsNone(ui.verified_ifiles)
        self.assertFalse(ui.options.is_verbose)
        self.assertFalse(ui.options.is_quiet)

        # # batch
        expected_ifiles = glob.glob(os_path.join(self.samples_dir, "*.txt"))
        expected_ifiles.extend(glob.glob(os_path.join(self.samples_dir, "*.docx")))
        expected_ifiles.extend(glob.glob(os_path.join(self.samples_dir, "*.odt")))
        map(os_path.abspath, expected_ifiles)

        args = ["nsca-lca", os_path.join(self.samples_dir, "*.txt")]
        ui.parse_args(args)
        assert ui.verified_ifiles is not None
        map(os_path.abspath, ui.verified_ifiles)
        self.assertCountEqual(ui.verified_ifiles, expected_ifiles)

        args = ["nsca-lca", self.samples_dir]
        ui.parse_args(args)
        assert ui.verified_ifiles is not None
        map(os_path.abspath, ui.verified_ifiles)
        self.assertCountEqual(ui.verified_ifiles, expected_ifiles)

        args = ["nsca-lca", self.samples_dir, os_path.join(self.project_dir, "img")]
        ui.parse_args(args)
        assert ui.verified_ifiles is not None
        map(os_path.abspath, ui.verified_ifiles)
        self.assertEqual(ui.verified_ifiles, expected_ifiles)
        self.assertCountEqual(ui.verified_ifiles, expected_ifiles)

        args = ["nsca-lca", os_path.join(self.project_dir, "img")]
        ui.parse_args(args)
        assert ui.verified_ifiles is not None
        map(os_path.abspath, ui.verified_ifiles)
        self.assertEqual(ui.verified_ifiles, [])

        # wordlist
        args = ["nsca-lca", filepath]
        ui.parse_args(args)
        self.assertEqual(ui.options.wordlist, "bnc")

        args = ["nsca-lca", filepath, "--wordlist", "bnc"]
        ui.parse_args(args)
        self.assertEqual(ui.options.wordlist, "bnc")

        args = ["nsca-lca", filepath, "--wordlist", "anc"]
        ui.parse_args(args)
        self.assertEqual(ui.options.wordlist, "anc")

        # tagset
        args = ["nsca-lca", filepath, "--tagset", "ud"]
        ui.parse_args(args)
        self.assertEqual(ui.options.tagset, "ud")

        args = ["nsca-lca", filepath]
        ui.parse_args(args)
        self.assertEqual(ui.options.tagset, "ud")

        args = ["nsca-lca", filepath, "--tagset", "ptb"]
        ui.parse_args(args)
        self.assertEqual(ui.options.tagset, "ptb")
