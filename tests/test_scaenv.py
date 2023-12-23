#!/usr/bin/env python3

import os

from neosca.ns_envar import getenv

from .cmdline_tmpl import BaseTmpl


class TestUtilEnv(BaseTmpl):
    def test_getenv(self):
        self.assertIsNone(getenv("NON_EXISTING_VAR"))
        os.environ["NON_EXISTING_DIR"] = "non_existing_directory"
        self.assertIsNone(getenv("NON_EXISTING_DIR"))
        os.environ["USER_HOME"] = os.path.expanduser("~")
        self.assertIsNotNone(getenv("USER_HOME"))
