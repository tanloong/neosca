#!/usr/bin/env python3

from itertools import islice
from typing import Iterable, Iterator, Optional, Tuple, Union

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
Ns_Procedure_Result = Tuple[bool, Optional[str]]


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


def safe_div(n1: Union[int, float], n2: Union[int, float]) -> Union[int, float]:
    """
    Safely divides two numbers.

    >>> safe_div(10, 2)
    5.0
    >>> safe_div(10, 0)
    0
    """
    return n1 / n2 if n2 else 0
