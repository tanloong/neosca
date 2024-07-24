#!/usr/bin/env python3

from collections.abc import Iterable, Iterator
from itertools import islice
from math import log as _log

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QWidget

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
Ns_Procedure_Result = tuple[bool, str | None]


def chunks(it: Iterable, size: int) -> Iterator:
    """
    Return an iterator that chunks the input iterable into sub-iterables of the specified size.

    >>> lst = list(range(6))
    >>> list(chunks(lst, 2))
    [(1, 2), (3, 4), (5, 6)]
    >>> list(chunks(lst, 5))
    [(1, 2, 3, 4, 5), (6,)]
    """
    # https://stackoverflow.com/a/22045226/20732031
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def safe_div(n1: int | float, n2: int | float) -> int | float:
    """
    Safely divides two numbers.

    >>> safe_div(10, 2)
    5.0
    >>> safe_div(10, 0)
    0
    """
    return n1 / n2 if n2 else 0


def safe_log(n: float, base: int | None = None) -> float:
    """
    >>> safe_log(10, 10)
    1.0
    >>> safe_log(10)
    2.302585092994046
    >>> safe_log(0)
    0
    """
    if n <= 0:
        return 0
    if base is not None:
        return _log(n, base)
    return _log(n)


def pt2px(pt: int | float, offset: int | float = 0) -> float:
    dpi = QGuiApplication.primaryScreen().physicalDotsPerInch()
    return (pt * dpi) / 72 + offset


# https://github.com/zealdocs/zeal/blob/9630cc94c155d87295e51b41fbab2bd5798f8229/src/libs/ui/mainwindow.cpp#L447
def bring_to_front(widget: QWidget) -> None:
    widget.show()
    widget.setWindowState(
        (widget.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive
    )
    widget.raise_()
    widget.activateWindow()
