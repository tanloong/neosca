#!/usr/bin/env python3

import os
import os.path as os_path
import platform
import sys

IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"
user_home = os_path.expanduser("~")
if IS_WINDOWS:
    user_name = os_path.basename(user_home)
    if user_name.isascii():
        USER_SOFTWARE_DIR = os.getenv("APPDATA", os_path.join(user_home, "AppData", "Roaming"))
    else:
        # if user_name contains non-latin chars, C:\
        USER_SOFTWARE_DIR = os_path.splitdrive(user_home)[0] + os_path.sep  # C:\
else:
    USER_SOFTWARE_DIR = os_path.join(user_home, ".local", "share")


# https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_utils/wl_misc.py#L80
def get_linux_distro():
    try:
        info = platform.freedesktop_os_release()  # New in Python 3.10
    except OSError:
        return "ubuntu"
    else:
        return info["ID"]
