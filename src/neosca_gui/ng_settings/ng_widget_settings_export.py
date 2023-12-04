#!/usr/bin/env python3

import os
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
from neosca_gui.ng_settings.ng_settings_default import available_export_types
from neosca_gui.ng_settings.ng_widget_settings_abstract import Ng_Widget_Settings_Abstract
from neosca_gui.ng_widgets.ng_widgets import Ng_LineEdit_Path, Ng_MessageBox_Confirm


class Ng_Widget_Settings_Export(Ng_Widget_Settings_Abstract):
    name = "Export"

    def __init__(self, main=None):
        super().__init__(main)
        self.setup_tables()

        self.gridlayout.addWidget(self.groupbox_tables, 0, 0)
        self.gridlayout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_tables(self) -> None:
        self.lineedit_path = Ng_LineEdit_Path()
        self.combobox_type = QComboBox()
        self.combobox_type.addItems(available_export_types)

        formlayout_tables = QFormLayout()
        formlayout_tables.addRow(QLabel("Default path:"), self.lineedit_path)
        formlayout_tables.addRow(QLabel("Default type:"), self.combobox_type)
        self.groupbox_tables = QGroupBox("Tables")
        self.groupbox_tables.setLayout(formlayout_tables)

    def load_settings(self) -> None:
        self.lineedit_path.setText(Ng_Settings.value(f"{self.name}/default-path"))
        self.combobox_type.setCurrentText(Ng_Settings.value(f"{self.name}/default-type"))

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
            ).exec()
            return False
        if not os_path.isdir(path):
            messagebox = Ng_MessageBox_Confirm(
                self,
                "Path Not Found",
                f'Found no existing directory named "{path}". Do you want to create the directory?',
                QMessageBox.Icon.Warning,
            )
            if messagebox.exec():
                os.makedirs(path)
                return True
            else:
                self.lineedit_path.setFocus()
                self.lineedit_path.selectAll()
                return False
        return True

    def apply_settings(self) -> None:
        Ng_Settings.setValue(f"{self.name}/default-path", self.lineedit_path.text())
        Ng_Settings.setValue(f"{self.name}/default-type", self.combobox_type.currentText())
