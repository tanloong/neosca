#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from .util_platform_info import IS_WINDOWS


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
if IS_WINDOWS:
    try:
        # https://stackoverflow.com/questions/36760127/...
        # how-to-use-the-new-support-for-ansi-escape-sequences-in-the-windows-10-console
        from ctypes import windll  # type:ignore

        kernel32 = windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:  # pragma: no cover
        color_support = False


def color_print(color: str, s: str, prefix: str = "", postfix: str = "", **kwargs) -> None:
    kwargs.update({"sep": ""})
    if color_support:
        print(prefix, bcolors.__getattribute__(color) + s + bcolors.ENDC, postfix, **kwargs)
    else:  # pragma: no cover
        print(prefix, s, postfix, **kwargs)


def same_line_print(s: str, width=80, **kwargs) -> None:
    print(f"\r{'':<{width}}", end="")  # clear the line
    print(f"\r{s}", end="", **kwargs)


def get_yes_or_no(prompt: str = "") -> str:
    prompt_options = "Enter [y]es or [n]o: "
    sep = "\n" if prompt else ""
    answer = input(prompt + sep + prompt_options)
    while answer not in ("y", "n", "Y", "N"):
        answer = input(f"Unexpected input: {answer}.\nEnter [y]es or [n]o: ")
    return answer
