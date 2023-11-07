#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import Optional, Tuple

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
SCAProcedureResult = Tuple[bool, Optional[str]]
