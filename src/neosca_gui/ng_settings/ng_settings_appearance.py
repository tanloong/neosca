#!/usr/bin/env python3

from typing import Dict

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QCheckBox,
    QFontComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QWidget,
)

from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_widgets import Ng_Combobox_Editable


class Ng_Widget_Settings_Appearance(QWidget):
    name = "Appearance"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.setup_font()

        self.grid_layout.addWidget(self.groupbox_font, 0, 0)
        self.grid_layout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_font(self):
        self.name_writing_system_mapping: Dict[str, QFontDatabase.WritingSystem] = {
            "Any": QFontDatabase.WritingSystem.Any
        }
        self.name_writing_system_mapping.update(
            {QFontDatabase.writingSystemName(ws): ws for ws in QFontDatabase.writingSystems()}
        )
        self.combobox_writing_system = Ng_Combobox_Editable()
        self.combobox_writing_system.addItems(tuple(self.name_writing_system_mapping.keys()))
        self.combobox_writing_system.setCurrentText("Any")
        self.combobox_family = QFontComboBox()
        self.spinbox_point_size = QSpinBox()
        self.spinbox_point_size.setRange(6, 20)
        self.checkbox_italic = QCheckBox("Italic")
        self.checkbox_bold = QCheckBox("Bold")
        self.gridlayout_font_style = QGridLayout()
        self.gridlayout_font_style.addWidget(self.checkbox_italic, 0, 0)
        self.gridlayout_font_style.addWidget(self.checkbox_bold, 0, 1)

        # Set current values
        family = Ng_Settings.value("Appearance/font-family")
        self.combobox_family.setCurrentText(family)
        # If previously set font doesn't has italic or bold style, disable the according checkbox
        self.update_italic_and_bold(family)
        self.checkbox_italic.setChecked(Ng_Settings.value("Appearance/font-italic", type=bool))
        self.checkbox_bold.setChecked(Ng_Settings.value("Appearance/font-bold", type=bool))
        self.spinbox_point_size.setValue(Ng_Settings.value("Appearance/font-size", type=int))

        # Bind
        self.combobox_writing_system.currentTextChanged.connect(self.update_available_font_families)
        self.combobox_family.currentTextChanged.connect(self.update_italic_and_bold)

        formlayout_font = QFormLayout()
        formlayout_font.addRow(QLabel("Writing system:"), self.combobox_writing_system)
        formlayout_font.addRow(QLabel("Font family:"), self.combobox_family)
        formlayout_font.addRow(QLabel("Font size:"), self.spinbox_point_size)
        formlayout_font.addRow(QLabel("Font style:"), self.gridlayout_font_style)
        self.groupbox_font = QGroupBox("Font")
        self.groupbox_font.setLayout(formlayout_font)

    def update_available_font_families(self, name: str):
        if name in self.name_writing_system_mapping:
            self.combobox_family.setWritingSystem(self.name_writing_system_mapping[name])

    def update_italic_and_bold(self, family: str):
        available_styles = QFontDatabase.styles(family)
        if "Italic" in available_styles:
            self.checkbox_italic.setEnabled(True)
        else:
            self.checkbox_italic.setChecked(False)
            self.checkbox_italic.setEnabled(False)
        if "Bold" in available_styles:
            self.checkbox_bold.setEnabled(True)
        else:
            self.checkbox_bold.setChecked(False)
            self.checkbox_bold.setEnabled(False)
