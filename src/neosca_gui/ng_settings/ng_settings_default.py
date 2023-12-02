#!/usr/bin/env python3

from neosca_gui import DESKTOP_PATH
from neosca_gui.ng_platform_info import IS_MAC, IS_WINDOWS, get_linux_distro

# https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_settings/wl_settings_default.py

# > The following settings need to be loaded before initialization of the main window
DEFAULT_INTERFACE_SCALING = "100%"

# > Font family
if IS_WINDOWS:
    DEFAULT_FONT_FAMILY = "Arial"
elif IS_MAC:
    # > SF Pro is the system font on macOS >= 10.11 but is not installed by default
    DEFAULT_FONT_FAMILY = "Helvetica Neue"
else:
    linux_distro_font_family_mapping = {"ubuntu": "Ubuntu", "debian": "DejaVu", "arch": "Noto Sans"}
    linux_distro = get_linux_distro()
    DEFAULT_FONT_FAMILY = (
        linux_distro_font_family_mapping[linux_distro]
        if linux_distro in linux_distro_font_family_mapping
        else "Ubuntu"
    )

# > Font size
if IS_WINDOWS:
    DEFAULT_FONT_SIZE = 9
elif IS_MAC:
    DEFAULT_FONT_SIZE = 13
else:
    DEFAULT_FONT_SIZE = 11


available_import_types = ("Text files (*.txt)", "Docx files (*.docx)", "Odt files (*.odt)", "All files (*)")
available_export_types = ("Excel Workbook (*.xlsx)", "CSV File (*.csv)", "TSV File (*.tsv)")
settings_default = {
    "Appearance/interface-scaling": DEFAULT_INTERFACE_SCALING,
    "Appearance/font-family": DEFAULT_FONT_FAMILY,
    "Appearance/font-size": DEFAULT_FONT_SIZE,
    "Appearance/font-size-min": 6,
    "Appearance/font-size-max": 20,
    "Appearance/font-italic": False,
    "Appearance/font-bold": False,
    "Appearance/triangle-height-ratio": 0.23,
    "Import/default-path": str(DESKTOP_PATH),
    "Import/default-type": available_import_types[0],
    "Export/default-path": str(DESKTOP_PATH),
    "Export/default-type": available_export_types[0],
}
