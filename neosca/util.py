#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import subprocess
import sys
from typing import Optional, Tuple


# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
SCAProcedureResult = Tuple[bool, Optional[str]]


class _bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


bcolors = _bcolors()
color_support = True
if sys.platform == "win32":
    try:
        # https://stackoverflow.com/questions/36760127/...
        # how-to-use-the-new-support-for-ansi-escape-sequences-in-the-windows-10-console
        from ctypes import windll

        kernel32 = windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:  # pragma: no cover
        color_support = False


def color_print(color, s: str, **kwargs) -> None:
    if color_support:
        print(bcolors.__getattribute__(color) + s + bcolors.ENDC, **kwargs)
    else:  # pragma: no cover
        print(s)


def try_write(filename: str, content: Optional[str]) -> SCAProcedureResult:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            if content is not None:
                f.write(content)
            return True, None
    except PermissionError:
        return (
            False,
            f"PermissionError: can not write to {filename}, because it is already"
            f" in use by another process.\n\n1. Ensure that {filename} is closed,"
            " or \n2. Specify another output filename through the `-o` option,"
            f" e.g. nsca input.txt -o {filename.replace('.csv', '-2.csv')}",
        )


def setenv(env_var: str, path: str, mode: str) -> None:
    """append the given path to the an environment variable"""
    if mode not in ("a", "w"):
        print(f"Unexpected mode: {mode}")
        sys.exit(1)
    current_value = os.environ.get(env_var, default="")
    if path not in current_value:
        if sys.platform == "win32":
            if mode == "a":
                subprocess.run(f'SETX {env_var} {current_value};"{path}"', shell=True)
            else:
                subprocess.run(f'SETX {env_var} "{path}"', shell=True)
        elif sys.platform in ("darwin", "linux"):
            shell = os.environ.get("SHELL")
            if shell is None:
                print(
                    "Failed to permanently append {path} to {env_var}.\nReason: can't detect"
                    " current shell."
                )
                sys.exit(1)
            else:
                startup_file_dict = {
                    "bash": "~/.bash_profile" if sys.platform == "darwin" else "~/.bashrc",
                    "zsh": "~/.zshrc",
                    "ksh": "~/.kshrc",
                    "tcsh": "~/.tcshrc",
                    "csh": "~/.cshrc",
                    "yash": "~/.yashrc",
                    "fish": "~/.config/fish/config.fish",
                    "ion": "~/.config/ion/initrc",
                }
                startup_file = startup_file_dict.get(os.path.basename(shell), None)
                if startup_file is None:
                    print(
                        f"Failed to permanently append {path} to {env_var}.\nReason: can't detect"
                        f" rc file for {shell}."
                    )
                    sys.exit(1)
                else:
                    with open(os.path.expanduser(startup_file), "a", encoding="utf-8") as f:
                        if mode == "a":
                            f.write(f'\nexport {env_var}=${env_var}:"{path}"\n')
                        else:
                            f.write(f'\nexport {env_var}="{path}"\n')
        else:
            print(f"Unsupported platform: {sys.platform}")
            sys.exit(1)
