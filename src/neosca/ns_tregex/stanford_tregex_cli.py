#!/usr/bin/env python3

import os
import subprocess
import sys
from subprocess import CalledProcessError

from ..ns_envar import STANFORD_TREGEX_HOME, get_dir_frm_env


def tregex_cli():
    stanford_tregex_home = get_dir_frm_env(STANFORD_TREGEX_HOME)
    if stanford_tregex_home is None:
        print(
            f"Error: The environment variable {STANFORD_TREGEX_HOME} is not found or "
            "its value is not an existing directory."
        )
        sys.exit(1)

    command = [
        "java",
        "-mx100m",
        "-cp",
        f"{stanford_tregex_home}{os.path.sep}stanford-tregex.jar{os.pathsep}",
        "edu.stanford.nlp.trees.tregex.TregexPattern",
    ] + sys.argv[1:]

    try:
        subprocess.run(command, check=True, capture_output=False)
    except CalledProcessError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    tregex_cli()
