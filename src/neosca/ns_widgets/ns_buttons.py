#!/usr/bin/env python3

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton


class NsPushButton(QPushButton):
    def __init__(self, text: str, enabled: bool = True, parent=None):
        super().__init__(text, parent)
        self.setEnabled(enabled)


class NsPushButtonIcon(NsPushButton):
    def __init__(self, icon: QIcon, text: str, enabled: bool = True, parent=None):
        super().__init__(text, enabled, parent)
        self.setIcon(icon)
