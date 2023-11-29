#!/usr/bin/env python3

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_settings.ng_settings_default import available_import_types
from neosca_gui.ng_widgets import Ng_LineEdit_Path


class Ng_Widget_Settings_Import(QWidget):
    name = "Import"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.setup_files()

        self.grid_layout.addWidget(self.groupbox_files, 0, 0)
        self.grid_layout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_files(self):
        lineedit_path = Ng_LineEdit_Path()
        combobox_type = QComboBox()
        combobox_type.addItems(available_import_types)

        # Set current values
        lineedit_path.setText(Ng_Settings.value("Import/default-path"))
        combobox_type.setCurrentText(Ng_Settings.value("Import/default-type"))

        formlayout_files = QFormLayout()
        formlayout_files.addRow(QLabel("Default path:"), lineedit_path)
        formlayout_files.addRow(QLabel("Default type:"), combobox_type)
        self.groupbox_files = QGroupBox("Files")
        self.groupbox_files.setLayout(formlayout_files)
