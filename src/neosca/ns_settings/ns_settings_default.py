#!/usr/bin/env python3

from neosca import DESKTOP_PATH
from neosca.ns_platform_info import IS_MAC, IS_WINDOWS, get_linux_distro

# https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_settings/wl_settings_default.py

# > The following settings need to be loaded before initialization of the main window
DEFAULT_SCALING = "100%"

# > Font family
if IS_WINDOWS:
    DEFAULT_FONT_FAMILY = "Arial"
elif IS_MAC:
    # > SF Pro is the system font on macOS >= 10.11 but is not installed by default
    DEFAULT_FONT_FAMILY = "Helvetica Neue"
else:
    linux_distro_font_family_mapping = {"ubuntu": "Ubuntu", "debian": "DejaVu", "arch": "Noto Sans"}
    linux_distro = get_linux_distro()
    DEFAULT_FONT_FAMILY = linux_distro_font_family_mapping.get(linux_distro, "Ubuntu")

# > Font size
if IS_WINDOWS:
    DEFAULT_FONT_SIZE = 9
elif IS_MAC:
    DEFAULT_FONT_SIZE = 13
else:
    DEFAULT_FONT_SIZE = 11


available_import_types = ("All files (*)", "Text files (*.txt)", "Docx files (*.docx)", "Odt files (*.odt)")
available_export_types = ("Excel Workbook (*.xlsx)", "CSV File (*.csv)", "TSV File (*.tsv)")
settings_default = {
    "Appearance/scaling": DEFAULT_SCALING,
    "Appearance/font-family": DEFAULT_FONT_FAMILY,
    "Appearance/font-size": DEFAULT_FONT_SIZE,
    "Appearance/font-size-min": 6,
    "Appearance/font-size-max": 20,
    "Appearance/font-italic": False,
    "Appearance/font-bold": False,
    "Appearance/triangle-height-ratio": 0.23,
    "Import/default-path": str(DESKTOP_PATH),
    "Import/default-type": available_import_types[0],
    "Import/include-files-in-subfolders": True,
    "Export/default-path": str(DESKTOP_PATH),
    "Export/default-type": available_export_types[0],
    "Lexical Complexity Analyzer/wordlist": "bnc",
    "Lexical Complexity Analyzer/tagset": "ud",
    "Miscellaneous/dont-warn-on-exit": False,
    "Miscellaneous/dont-warn-on-cache-deletion": False,
    "Miscellaneous/cache": True,
    "Miscellaneous/use-cache": True,
    "default-splitter-sca": 200,
    "default-splitter-lca": 200,
    "default-splitter-file": 150,
    "show-statusbar": True,
}
