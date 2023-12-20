#!/usr/bin/env python3

import sys
from pathlib import Path

SRC_DIR: Path = Path(__file__).parent.parent.absolute() / "src"
sys.path.insert(0, str(SRC_DIR))
