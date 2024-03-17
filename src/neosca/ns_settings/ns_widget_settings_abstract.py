#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QWidget


class Ns_Widget_Settings_Abstract(QWidget):
    name: str = ""

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
