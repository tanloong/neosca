#!/usr/bin/env python

import sys
from pathlib import Path

NEOSCA_HOME: Path = Path(__file__).parent.absolute()
DESKTOP_PATH: Path = Path.home().absolute() / "Desktop"
DATA_FOLDER: Path = NEOSCA_HOME / "data"
SETTING_PATH: Path = NEOSCA_HOME / "settings.ini"
QSS_PATH = NEOSCA_HOME / "ng_style.qss"

sys.path.insert(0, str(NEOSCA_HOME))
