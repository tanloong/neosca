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

from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_settings.ng_settings_default import available_import_types
from neosca_gui.ng_settings.ng_widget_settings_abstract import Ng_Widget_Settings_Abstract
from neosca_gui.ng_widgets.ng_widgets import Ng_LineEdit_Path


class Ng_Widget_Settings_Import(Ng_Widget_Settings_Abstract):
    name: str = "Import"

    def __init__(self, main=None):
        super().__init__(main)
        self.setup_files()

        self.gridlayout.addWidget(self.groupbox_files, 0, 0)
        self.gridlayout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_files(self) -> None:
        self.lineedit_path = Ng_LineEdit_Path()
        self.combobox_type = QComboBox()
        self.combobox_type.addItems(available_import_types)

        formlayout_files = QFormLayout()
        formlayout_files.addRow(QLabel("Default path:"), self.lineedit_path)
        formlayout_files.addRow(QLabel("Default type:"), self.combobox_type)
        self.groupbox_files = QGroupBox("Files")
        self.groupbox_files.setLayout(formlayout_files)

    def load_settings(self) -> None:
        self.lineedit_path.setText(Ng_Settings.value(f"{self.name}/default-path"))
        self.combobox_type.setCurrentText(Ng_Settings.value(f"{self.name}/default-type"))

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
            ).exec()
            return False
        if not os_path.isdir(path):
            self.lineedit_path.setFocus()
            self.lineedit_path.selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Path Not Found",
                f'Found no existing directory named "{path}". Please check and try again.',
                QMessageBox.StandardButton.Ok,
                self,
            ).exec()
            return False
        return True

    def apply_settings(self) -> None:
        Ng_Settings.setValue(f"{self.name}/default-path", self.lineedit_path.text())
        Ng_Settings.setValue(f"{self.name}/default-type", self.combobox_type.currentText())
