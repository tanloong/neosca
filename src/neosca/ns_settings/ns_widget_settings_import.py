#!/usr/bin/env python3

import os.path as os_path

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
)

from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_settings.ns_settings_default import available_import_types
from neosca.ns_settings.ns_widget_settings_abstract import Ns_Widget_Settings_Abstract
from neosca.ns_widgets.ns_widgets import Ns_LineEdit_Path


class Ns_Widget_Settings_Import(Ns_Widget_Settings_Abstract):
    name: str = "Import"

    def __init__(self, main=None):
        super().__init__(main)
        self.setup_files()

        self.gridlayout.addWidget(self.groupbox_files, 0, 0)
        self.gridlayout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_files(self) -> None:
        self.lineedit_path = Ns_LineEdit_Path()
        self.combobox_type = QComboBox()
        self.combobox_type.addItems(available_import_types)

        formlayout_files = QFormLayout()
        formlayout_files.addRow(QLabel("Default path:"), self.lineedit_path)
        formlayout_files.addRow(QLabel("Default type:"), self.combobox_type)
        self.groupbox_files = QGroupBox("Files")
        self.groupbox_files.setLayout(formlayout_files)

    def load_settings(self) -> None:
        self.lineedit_path.setText(Ns_Settings.value(f"{self.name}/default-path"))
        self.combobox_type.setCurrentText(Ns_Settings.value(f"{self.name}/default-type"))

    def verify_settings(self) -> bool:
        path = self.lineedit_path.text()
        if not path or path.isspace():
            self.lineedit_path.setFocus()
            self.lineedit_path.selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Empty Path",
                "The path should not be left empty.",
                QMessageBox.StandardButton.Ok,
                self,
            ).open()
            return False
        if not os_path.isdir(path):
            self.lineedit_path.setFocus()
            self.lineedit_path.selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Path Not Found",
                f'The specified directory "{path}" could not be found. Please check and try again.',
                QMessageBox.StandardButton.Ok,
                self,
            ).exec()
            return False
        return True

    def apply_settings(self) -> None:
        Ns_Settings.setValue(f"{self.name}/default-path", self.lineedit_path.text())
        Ns_Settings.setValue(f"{self.name}/default-type", self.combobox_type.currentText())
