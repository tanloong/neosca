#!/usr/bin/env python

import sys
from pathlib import Path

NEOSCA_HOME: Path = Path(__file__).parent.absolute()
SETTING_PATH: Path = NEOSCA_HOME / "settings.ini"

DATA_FOLDER: Path = NEOSCA_HOME / "data"
QSS_PATH: Path = DATA_FOLDER / "ng_style.qss"
CITING_PATH: Path = DATA_FOLDER / "citing.json"

DESKTOP_PATH: Path = Path.home().absolute() / "Desktop"

sys.path.insert(0, str(NEOSCA_HOME))
