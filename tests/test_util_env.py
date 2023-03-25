#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
from .cmdline_tmpl import BaseTmpl
from neosca.util_env import getenv


class TestUtilEnv(BaseTmpl):
    def test_getenv(self):
        self.assertIsNone(getenv("NON_EXISTING_VAR"))
        os.environ["NON_EXISTING_DIR"] = "non_existing_directory"
        self.assertIsNone(getenv("NON_EXISTING_DIR"))
        os.environ["USER_HOME"] = os.path.expanduser("~")
        self.assertIsNotNone(getenv("USER_HOME"))
