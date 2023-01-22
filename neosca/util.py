#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import sys
from typing import Optional, Tuple, List


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


def same_line_print(s: str, width=80, **kwargs) -> None:
    print(f"\r{'':<{width}}", end="")  # clear the line
    print(f"\r{s}", end="", **kwargs)


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


def _setenv_windows(env_var: str, paths: List[str], refresh: bool = False) -> None:
    import winreg  # Allows access to the windows registry
    import ctypes  # Allows interface with low-level C API's

    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:  # type:ignore
        # Get the current user registry
        with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:  # type:ignore
            # Go to the environment key
            if refresh or os.environ.get(env_var) is None:
                new_value = ";".join(paths)
            else:
                existing_value = os.environ.get(env_var)
                new_value = existing_value + ";" + ";".join(paths)  # type:ignore
                # Takes the current path value and appends the new program path
            winreg.SetValueEx(key, env_var, 0, winreg.REG_EXPAND_SZ, new_value)  # type:ignore
            # Updated the path with the updated path

        # Tell other processes to update their environment
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW  # type:ignore
        SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result),
        )


def _setenv_unix(env_var: str, paths: List[str], refresh: bool = False) -> None:
    shell = os.environ.get("SHELL")
    if shell is None:
        print("Failed to permanently append {path} to {env_var}.\nReason: can't detect current shell.")
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
                f"Failed to permanently set environment variables.\nReason: can't detect rc file for {shell}."
            )
            sys.exit(1)
        else:
            new_paths = ":".join(paths)
            with open(os.path.expanduser(startup_file), "a", encoding="utf-8") as f:
                if refresh:
                    f.write(f'\nexport {env_var}="{new_paths}"')
                else:
                    f.write(f'\nexport {env_var}=${env_var}:"{new_paths}"')


def setenv(env_var: str, paths: List[str], refresh: bool = False) -> None:
    assert sys.platform in ("win32", "darwin", "linux")
    if sys.platform == "win32":
        _setenv_windows(env_var, paths, refresh)
    else:
        _setenv_unix(env_var, paths, refresh)
    print(f"Added the following path(s) to {env_var}:\n", "\n".join(paths), sep="")
