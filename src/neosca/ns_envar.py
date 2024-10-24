#!/usr/bin/env python3

import logging
import os
import os.path as os_path

from .ns_platform_info import IS_LINUX, IS_MAC, IS_WINDOWS
from .ns_print import color_print

# JAVA_HOME = "JAVA_HOME"
# STANFORD_PARSER_HOME = "STANFORD_PARSER_HOME"
STANFORD_TREGEX_HOME = "STANFORD_TREGEX_HOME"


def _setenv_windows(env_var: str, paths: list[str], is_refresh: bool = False) -> None:
    import ctypes  # Allows interface with low-level C API's
    import winreg  # Allows access to the windows registry

    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:  # type:ignore
        # Get the current user registry
        with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:  # type:ignore
            # Go to the environment key
            if is_refresh or os.environ.get(env_var) is None:
                new_value = ";".join(paths)
            else:
                existins_value = os.environ.get(env_var)
                new_value = existins_value + ";" + ";".join(paths)  # type:ignore
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


def _setenv_unix(env_var: str, paths: list[str], is_refresh: bool = False) -> None:
    shell = os.environ.get("SHELL")
    if shell is None:
        logging.warning(
            "Failed to permanently append {path} to {env_var}.\nReason: can't detect current" " shell."
        )
    else:
        shell_rcfile = {
            "bash": "~/.bash_profile" if IS_MAC else "~/.bashrc",
            "zsh": "~/.zshrc",
            "ksh": "~/.kshrc",
            "tcsh": "~/.tcshrc",
            "csh": "~/.cshrc",
            "yash": "~/.yashrc",
            "fish": "~/.config/fish/config.fish",
            "ion": "~/.config/ion/initrc",
        }
        rcfile = shell_rcfile.get(os_path.basename(shell), None)
        if rcfile is None:
            logging.warning(
                "Failed to permanently set environment variables.\nReason: can't detect rc"
                f" file for {shell}."
            )
        else:
            new_paths = '"' + '":"'.join(paths) + '"'
            rcfile = os_path.expanduser(rcfile)
            os.makedirs(os_path.realpath(os_path.dirname(rcfile)), exist_ok=True)

            if not os_path.isfile(rcfile):
                configs = []
            else:
                with open(rcfile, encoding="utf-8") as f:
                    configs = [line.strip() for line in f.readlines()]
            new_config = (
                f"export {env_var}={new_paths}" if is_refresh else f"export {env_var}=${env_var}:{new_paths}"
            )
            duplicated_config_index = []
            for i, config in enumerate(configs):
                if is_refresh:
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


def setenv(envar: str, paths: list[str], is_override: bool = False, is_quiet: bool = False) -> None:
    assert any((IS_WINDOWS, IS_MAC, IS_LINUX))
    if IS_WINDOWS:
        _setenv_windows(envar, paths, is_override)
    else:
        _setenv_unix(envar, paths, is_override)
    if not is_quiet:
        color_print(
            "OKGREEN",
            envar,
            prefix="Added the following path(s) to ",
            postfix=":\n" + "\n".join(paths),
        )


def get_dir_frm_env(envar: str) -> str | None:
    directory = os.getenv(envar, "")
    return directory if os_path.isdir(directory) else None
