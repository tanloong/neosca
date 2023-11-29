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
from neosca_gui.ng_settings.ng_settings_default import available_export_types
from neosca_gui.ng_widgets import Ng_LineEdit_Path


class Ng_Widget_Settings_Export(QWidget):
    name = "Export"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.setup_tables()

        self.grid_layout.addWidget(self.groupbox_tables, 0, 0)
        self.grid_layout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_tables(self):
        lineedit_path = Ng_LineEdit_Path()
        combobox_type = QComboBox()
        combobox_type.addItems(available_export_types)

        # Set current values
        lineedit_path.setText(Ng_Settings.value("Export/default-path"))
        combobox_type.setCurrentText(Ng_Settings.value("Export/default-type"))

        formlayout_tables = QFormLayout()
        formlayout_tables.addRow(QLabel("Default path:"), lineedit_path)
        formlayout_tables.addRow(QLabel("Default type:"), combobox_type)
        self.groupbox_tables = QGroupBox("Tables")
        self.groupbox_tables.setLayout(formlayout_tables)
