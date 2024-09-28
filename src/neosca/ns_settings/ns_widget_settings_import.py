#!/usr/bin/env python3

import os.path as os_path

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
)

from ..ns_settings.ns_settings import Ns_Settings
from ..ns_settings.ns_settings_default import available_import_types
from ..ns_settings.ns_widget_settings_abstract import Ns_Widget_Settings_Abstract
from ..ns_widgets.ns_widgets import Ns_LineEdit_Path


class Ns_Widget_Settings_Import(Ns_Widget_Settings_Abstract):
    name: str = "Import"

    def __init__(self, main=None):
        super().__init__(main)
        self.setup_files()

        self.gridlayout.addWidget(self.groupbox_files, 0, 0)
        self.gridlayout.setRowStretch(self.gridlayout.rowCount(), 1)

    def setup_files(self) -> None:
        self.lineedit_path = Ns_LineEdit_Path()
        self.combobox_type = QComboBox()
        self.combobox_type.addItems(available_import_types)
        self.checkbox_include_files_in_subfolders = QCheckBox("Include files in subfolders")

        gridlayout_files = QGridLayout()
        gridlayout_files.addWidget(QLabel("Default path:"), 0, 0)
        gridlayout_files.addWidget(self.lineedit_path, 0, 1)
        gridlayout_files.addWidget(QLabel("Default type:"), 1, 0)
        gridlayout_files.addWidget(self.combobox_type, 1, 1)
        gridlayout_files.addWidget(self.checkbox_include_files_in_subfolders, 2, 0, 1, 2)
        self.groupbox_files = QGroupBox("Files")
        self.groupbox_files.setLayout(gridlayout_files)

    def load_settings(self) -> None:
        self.lineedit_path.setText(Ns_Settings.value(f"{self.name}/default-path"))
        self.combobox_type.setCurrentText(Ns_Settings.value(f"{self.name}/default-type"))
        self.checkbox_include_files_in_subfolders.setChecked(
            Ns_Settings.value(f"{self.name}/include-files-in-subfolders", type=bool)
        )

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
        Ns_Settings.setValue(
            f"{self.name}/include-files-in-subfolders", self.checkbox_include_files_in_subfolders.isChecked()
        )
