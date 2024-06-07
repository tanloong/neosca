#!/usr/bin/env python3

import subprocess
from pathlib import Path

cmd = ["pyinstaller", str(Path(__file__).parent / "ns_packaging.spec"), "--noconfirm", "--clean"]

subprocess.run(cmd)
