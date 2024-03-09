#!/usr/bin/env python3

import os

from neosca.ns_envar import get_dir_frm_env

from .cmdline_tmpl import BaseTmpl


class TestUtilEnv(BaseTmpl):
    def test_getenv(self):
        # returns None for non-existent envar key
        self.assertIsNone(get_dir_frm_env("NON_EXISTING_VAR"))
        # returns None if the envar exists but its value is not an existent dir
        os.environ["NON_EXISTING_DIR"] = "non_existing_directory"
        self.assertIsNone(get_dir_frm_env("NON_EXISTING_DIR"))

        os.environ["USER_HOME"] = os.path.expanduser("~")
        self.assertIsNotNone(get_dir_frm_env("USER_HOME"))
