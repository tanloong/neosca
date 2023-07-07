#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import sys
import os

IS_WINDOWS = sys.platform == "win32"
IS_DARWIN = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"
user_home = os.path.expanduser("~")
if IS_WINDOWS:  # pragma: no cover
    user_name = os.path.basename(user_home)
    if user_name.isascii():
        USER_SOFTWARE_DIR = os.getenv("AppData", os.path.join(user_home, "AppData", "Roaming"))
    else:  # if user_name contains non-latin chars
        USER_SOFTWARE_DIR = os.path.splitdrive(user_home)[0] + os.path.sep  # C:\
else:
    USER_SOFTWARE_DIR = os.path.join(user_home, ".local", "share")
