#!/usr/bin/env python3

import platform
import sys

IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"


# https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_utils/wl_misc.py#L80
def get_linux_distro():
    try:
        info = platform.freedesktop_os_release()  # New in Python 3.10
    except OSError:
        return "ubuntu"
    else:
        return info["ID"]
