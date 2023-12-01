#!/usr/bin/env python3

from PySide6.QtWidgets import QGridLayout, QWidget


class Ng_Widget_Settings_Abstract(QWidget):
    name = None

    def __init__(self, main):
        super().__init__(main)
        self.main = main
        self.gridlayout = QGridLayout()
        self.setLayout(self.gridlayout)

    def load_settings(self) -> None:
        raise NotImplementedError

    def verify_settings(self) -> bool:
        raise NotImplementedError

    def apply_settings(self) -> None:
        raise NotImplementedError
