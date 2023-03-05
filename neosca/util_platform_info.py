#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import sys
import os

IS_WINDOWS = sys.platform == "win32"
IS_DARWIN = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"
if IS_WINDOWS and os.environ.get("AppData") is not None:
    USER_SOFTWARE_DIR = os.environ.get("AppData")
else:
    user_home = os.path.expanduser("~")
    USER_SOFTWARE_DIR = os.path.join(user_home, ".local", "share")
