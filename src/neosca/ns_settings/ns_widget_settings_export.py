#!/usr/bin/env python3

import os
import os.path as os_path

from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
)

from ..ns_settings.ns_settings import Ns_Settings
from ..ns_settings.ns_settings_default import available_export_types
from ..ns_settings.ns_widget_settings_abstract import Ns_Widget_Settings_Abstract
from ..ns_widgets.ns_widgets import Ns_LineEdit_Path, Ns_MessageBox_Question


class Ns_Widget_Settings_Export(Ns_Widget_Settings_Abstract):
    name: str = "Export"

    def __init__(self, main=None):
        super().__init__(main)
        self.setup_tables()

        self.gridlayout.addWidget(self.groupbox_tables, 0, 0)
        self.gridlayout.setRowStretch(self.gridlayout.rowCount(), 1)

    def setup_tables(self) -> None:
        self.lineedit_path = Ns_LineEdit_Path()
        self.combobox_type = QComboBox()
        self.combobox_type.addItems(available_export_types)

        gridlayout_tables = QGridLayout()
        gridlayout_tables.addWidget(QLabel("Default path:"), 0, 0)
        gridlayout_tables.addWidget(self.lineedit_path, 0, 1)
        gridlayout_tables.addWidget(QLabel("Default type:"), 1, 0)
        gridlayout_tables.addWidget(self.combobox_type, 1, 1)
        self.groupbox_tables = QGroupBox("Tables")
        self.groupbox_tables.setLayout(gridlayout_tables)

    def load_settings(self) -> None:
        self.lineedit_path.setText(Ns_Settings.value(f"{self.name}/default-path"))
        self.combobox_type.setCurrentText(Ns_Settings.value(f"{self.name}/default-type"))

    def verify_settings(self) -> bool:
        return self.verify_settings_tables()

    def verify_settings_tables(self) -> bool:
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
            messagebox = Ns_MessageBox_Question(
                self,
                "Path Not Found",
                f'The specified directory "{path}" could not be found. Do you want to create the directory?',
                QMessageBox.Icon.Warning,
            )
            if messagebox.exec() == QMessageBox.StandardButton.Yes:
                os.makedirs(path)
                return True
            else:
                self.lineedit_path.setFocus()
                self.lineedit_path.selectAll()
                return False
        return True

    def apply_settings(self) -> None:
        Ns_Settings.setValue(f"{self.name}/default-path", self.lineedit_path.text())
        Ns_Settings.setValue(f"{self.name}/default-type", self.combobox_type.currentText())
