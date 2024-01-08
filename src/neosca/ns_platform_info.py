#!/usr/bin/env python3

import platform
import sys
from pathlib import Path

from platformdirs import user_cache_path

from neosca.ns_about import __title__

IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform == "linux"

USER_CACHE_PATH: Path = user_cache_path(appname=__title__, ensure_exists=True)


# https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_utils/wl_misc.py#L80
def get_linux_distro():
    try:
        info = platform.freedesktop_os_release()  # New in Python 3.10
    except OSError:
        return "ubuntu"
    else:
        return info["ID"]
