import sys
from pathlib import PurePath

SRC_DIR = PurePath(__file__).parent.parent.joinpath("src")
sys.path.insert(0, str(SRC_DIR))
