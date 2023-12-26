#!/usr/bin/env python3

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton


class Ns_PushButton(QPushButton):
    def __init__(self, text: str, enabled: bool = True, parent=None):
        super().__init__(text, parent)
        self.setEnabled(enabled)


class Ns_PushButton_Icon(Ns_PushButton):
    def __init__(self, icon: QIcon, text: str, enabled: bool = True, parent=None):
        super().__init__(text, enabled, parent)
        self.setIcon(icon)
