#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
from typing import List, Optional, Tuple

from .util_platform_info import IS_DARWIN, IS_LINUX, IS_WINDOWS
from .util_print import color_print

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
SCAProcedureResult = Tuple[bool, Optional[str]]


def try_write(filename: str, content: Optional[str]) -> SCAProcedureResult:
    if not os.path.exists(filename):
        return True, None
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
        print(
            "Failed to permanently append {path} to {env_var}.\nReason: can't detect current"
            " shell."
        )
    else:
        shell_rcfile = {
            "bash": "~/.bash_profile" if IS_DARWIN else "~/.bashrc",
            "zsh": "~/.zshrc",
            "ksh": "~/.kshrc",
            "tcsh": "~/.tcshrc",
            "csh": "~/.cshrc",
            "yash": "~/.yashrc",
            "fish": "~/.config/fish/config.fish",
            "ion": "~/.config/ion/initrc",
        }
        rcfile = shell_rcfile.get(os.path.basename(shell), None)
        if rcfile is None:
            print(
                "Failed to permanently set environment variables.\nReason: can't detect rc"
                f" file for {shell}."
            )
        else:
            new_paths = '"' + '":"'.join(paths) + '"'
            rcfile = os.path.expanduser(rcfile)
            if not os.path.isfile(rcfile):
                configs = []
            else:
                with open(rcfile, "r", encoding="utf-8") as f:
                    configs = [line.strip() for line in f.readlines()]
            new_config = (
                f"export {env_var}={new_paths}"
                if refresh
                else f"export {env_var}=${env_var}:{new_paths}"
            )
            duplicated_config_index = []
            for i, config in enumerate(configs):
                if refresh:
                    if config.startswith(f"export {env_var}"):
                        duplicated_config_index.append(i)
                else:
                    if config == new_config:
                        duplicated_config_index.append(i)
            for i in duplicated_config_index:
                del configs[i]
            if duplicated_config_index:
                configs.insert(duplicated_config_index[0], new_config)
            else:
                configs.append(new_config)
            with open(rcfile, "w", encoding="utf-8") as f:
                f.write("\n".join(configs))


def setenv(env_var: str, paths: List[str], refresh: bool = False) -> None:
    assert any((IS_WINDOWS, IS_DARWIN, IS_LINUX))
    if IS_WINDOWS:
        _setenv_windows(env_var, paths, refresh)
    else:
        _setenv_unix(env_var, paths, refresh)
    color_print(
        "OKGREEN",
        env_var,
        prefix="Added the following path(s) to ",
        postfix=":\n" + "\n".join(paths),
        end="\n\n",
    )
