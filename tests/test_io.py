#!/usr/bin/env python3

from neosca.ns_io import Ns_IO

from .base_tmpl import BaseTmpl


class TestIO(BaseTmpl):
    def test_create_unique_filename(self):
        self.assertEqual(Ns_IO.ensure_unique_filestem("name", ["name"]), "name (2)")
        self.assertEqual(Ns_IO.ensure_unique_filestem("name", ["name", "name (1)"]), "name (2)")
        self.assertEqual(Ns_IO.ensure_unique_filestem("name", ["name", "name (1)", "name (2)"]), "name (3)")
        self.assertEqual(Ns_IO.ensure_unique_filestem("name", ["other"]), "name")
