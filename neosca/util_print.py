#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from .util_platform_info import IS_WINDOWS
import sys


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
if IS_WINDOWS:  # pragma: no cover
    try:
        # https://stackoverflow.com/questions/36760127/...
        # how-to-use-the-new-support-for-ansi-escape-sequences-in-the-windows-10-console
        from ctypes import windll  # type:ignore

        kernel32 = windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        color_support = False


def color_print(
    color: str, s: str, prefix: str = "", postfix: str = ""
) -> None:  # pragma: no cover
    if color_support:
        sys.stderr.write(prefix)
        sys.stderr.write(bcolors.__getattribute__(color) + s + bcolors.ENDC)
        sys.stderr.write(postfix + "\n")
    else:  # pragma: no cover
        sys.stderr.write(prefix)
        sys.stderr.write(s)
        sys.stderr.write(postfix + "\n")


def same_line_print(s: str, width=80) -> None:  # pragma: no cover
    sys.stderr.write(f"\r{'':<{width}}")  # clear the line
    sys.stderr.write(f"\r{s}")


def get_yes_or_no(prompt: str = "") -> str:  # pragma: no cover
    option = "Enter [y]es or [n]o: "
    sep = "\n" if prompt else ""
    answer = input(prompt + sep + option)
    while answer not in ("y", "n", "Y", "N", "yes", "Yes", "no", "No"):
        answer = input(f"Unexpected input: {answer}.\n{option}")
    return answer
