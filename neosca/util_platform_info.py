#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import sys
import os

IS_WINDOWS = sys.platform == "win32"
IS_DARWIN = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"
user_home = os.path.expanduser("~")
if IS_WINDOWS:  # pragma: no cover
    USER_SOFTWARE_DIR = os.getenv("AppData", os.path.join(user_home, "AppData", "Roaming"))
else:
    USER_SOFTWARE_DIR = os.path.join(user_home, ".local", "share")
