#!/usr/bin/env python3

from typing import Optional, Tuple

# For all the procedures in SCAUI, return a tuple as the result
# The first element bool indicates whether the procedure succeeds
# The second element is the error message if it fails.
Ns_Procedure_Result = Tuple[bool, Optional[str]]
