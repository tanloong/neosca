#!/usr/bin/env python

import sys
from pathlib import Path

SRC_DIR: Path = Path(__file__).parent.absolute()
# https://stackoverflow.com/a/13790741/20732031
attr = "_MEIPASS"
if hasattr(sys, attr):
    NEOSCA_DIR: Path = Path(getattr(sys, attr)).absolute()
else:
    NEOSCA_DIR: Path = SRC_DIR.parent.parent

SETTING_PATH: Path = NEOSCA_DIR / "settings.ini"

IMG_DIR: Path = NEOSCA_DIR / "imgs"
ICON_PATH: Path = IMG_DIR / "ns_icon.ico"
ICON_MAC_PATH: Path = IMG_DIR / "ns_icon.icns"

DATA_DIR: Path = NEOSCA_DIR / "data"
QSS_PATH: Path = DATA_DIR / "ns_style.qss"
CITING_PATH: Path = DATA_DIR / "citing.json"
STANZA_MODEL_DIR: Path = DATA_DIR / "stanza_resources"

DESKTOP_PATH: Path = Path.home().absolute() / "Desktop"

sys.path.insert(0, str(SRC_DIR))
