#!/usr/bin/env python3

from .ng_platform_info import IS_MAC, IS_WINDOWS, get_linux_distro

# https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_settings/wl_settings_default.py
# > The following settings need to be loaded before initialization of the main window
DEFAULT_INTERFACE_SCALING = "100%"

# > Font family
if IS_WINDOWS:
    DEFAULT_FONT_FAMILY = "Arial"
elif IS_MAC:
    # SF Pro is the system font on macOS >= 10.11 but is not installed by default
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

settings_default = {
    "general": {
        "ui_settings": {
            "interface_scaling": DEFAULT_INTERFACE_SCALING,
            "font_family": DEFAULT_FONT_FAMILY,
            "font_size": DEFAULT_FONT_SIZE,
        }
    }
}
