#!/usr/bin/env python

import sys

from .ns_about import __version__
from .ns_consts import PKG_DIR

sys.path.insert(0, str(PKG_DIR))

__all__ = ["__version__"]
