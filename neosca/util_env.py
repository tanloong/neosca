#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import glob
import logging
import os
from typing import List, Optional

from .util_platform_info import IS_DARWIN, IS_LINUX, IS_WINDOWS
from .util_print import color_print


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
        logging.warning(
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
            logging.warning(
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


def setenv(
    env_var: str, paths: List[str], refresh: bool = False, is_quiet: bool = False
) -> None:
    assert any((IS_WINDOWS, IS_DARWIN, IS_LINUX))
    if IS_WINDOWS:
        _setenv_windows(env_var, paths, refresh)
    else:
        _setenv_unix(env_var, paths, refresh)
    if not is_quiet:
        color_print(
            "OKGREEN",
            env_var,
            prefix="Added the following path(s) to ",
            postfix=":\n" + "\n".join(paths),
        )


def getenv(env_var: str) -> Optional[str]:
    directory = os.getenv(env_var, "")
    return directory if os.path.isdir(directory) else None


def search_java_home() -> Optional[str]:
    candidate = None
    paths = os.getenv("PATH", "").split(os.pathsep)
    for dir_name in paths:
        if os.path.basename(dir_name) == "bin":
            if glob.glob(os.path.join(dir_name, "java.*")):
                candidate = os.path.dirname(dir_name)
                break
    if candidate is None and IS_WINDOWS:
        system_software_dir = os.getenv("ProgramFiles", "")
        if glob.glob(os.path.join(system_software_dir, "Java", "j[dr][ke]*")):
            candidate = glob.glob(os.path.join(system_software_dir, "Java", "j[dr][ke]*"))[0]
    return candidate
