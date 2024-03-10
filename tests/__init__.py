import sys
from pathlib import PurePath

from PySide6.QtWidgets import QApplication

SRC_DIR = PurePath(__file__).parent.parent.joinpath("src")
sys.path.insert(0, str(SRC_DIR))

ns_app = QApplication()
