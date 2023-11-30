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
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
)

from neosca_gui.ng_qss import Ng_QSS
from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_settings.ng_widget_settings_abstract import Ng_Widget_Settings_Abstract
from neosca_gui.ng_widgets import Ng_Combobox_Editable


class Ng_Widget_Settings_Appearance(Ng_Widget_Settings_Abstract):
    name = "Appearance"

    def __init__(self, main):
        super().__init__(main)
        self.setup_font()

        self.gridlayout.addWidget(self.groupbox_font, 0, 0)
        self.gridlayout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_font(self) -> None:
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
        self.spinbox_point_size.setSuffix(" pt")
        self.spinbox_point_size.setRange(6, 20)
        self.checkbox_italic = QCheckBox("Italic")
        self.checkbox_bold = QCheckBox("Bold")
        self.gridlayout_font_style = QGridLayout()
        self.gridlayout_font_style.addWidget(self.checkbox_italic, 0, 0)
        self.gridlayout_font_style.addWidget(self.checkbox_bold, 0, 1)

        # Bind
        self.combobox_writing_system.currentTextChanged.connect(self.update_available_font_families)
        self.combobox_family.currentTextChanged.connect(self.set_italic_bold_enabled)

        formlayout_font = QFormLayout()
        formlayout_font.addRow(QLabel("Writing system:"), self.combobox_writing_system)
        formlayout_font.addRow(QLabel("Font family:"), self.combobox_family)
        formlayout_font.addRow(QLabel("Font size:"), self.spinbox_point_size)
        formlayout_font.addRow(QLabel("Font style:"), self.gridlayout_font_style)
        self.groupbox_font = QGroupBox("Font")
        self.groupbox_font.setLayout(formlayout_font)

    def update_available_font_families(self, name: str) -> None:
        if name in self.name_writing_system_mapping:
            self.combobox_family.setEnabled(True)
            self.spinbox_point_size.setEnabled(True)
            self.set_italic_bold_enabled(self.combobox_family.currentText())

            self.combobox_family.setWritingSystem(self.name_writing_system_mapping[name])

            current_family = Ng_Settings.value("Appearance/font-family")
            contains_current_family = any(
                current_family == self.combobox_family.itemText(i) for i in range(self.combobox_family.count())
            )
            if contains_current_family:
                self.combobox_family.setCurrentText(current_family)
        else:
            self.combobox_family.setEnabled(False)
            self.spinbox_point_size.setEnabled(False)
            self.checkbox_italic.setEnabled(False)
            self.checkbox_bold.setEnabled(False)

    def set_italic_bold_enabled(self, family: str) -> None:
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

    def load_settings(self) -> None:
        family = Ng_Settings.value("Appearance/font-family")
        self.combobox_family.setCurrentText(family)
        # If previously set font doesn't has italic or bold style, disable the according checkbox
        self.set_italic_bold_enabled(family)
        self.checkbox_italic.setChecked(Ng_Settings.value(f"{self.name}/font-italic", type=bool))
        self.checkbox_bold.setChecked(Ng_Settings.value(f"{self.name}/font-bold", type=bool))
        self.spinbox_point_size.setValue(Ng_Settings.value(f"{self.name}/font-size", type=int))

    def verify_settings(self) -> bool:
        writing_system_name = self.combobox_writing_system.currentText()
        if writing_system_name.isspace():
            self.combobox_writing_system.lineEdit().setFocus()
            self.combobox_writing_system.lineEdit().selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Empty Writing System",
                "Writing system should not be left empty.",
                QMessageBox.StandardButton.Ok,
                self,
            ).exec()
            return False
        if writing_system_name not in self.name_writing_system_mapping:
            self.combobox_writing_system.lineEdit().setFocus()
            self.combobox_writing_system.lineEdit().selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Writing System Not Found",
                f'Found no writing system named "{writing_system_name}". Please check and try again.',
                QMessageBox.StandardButton.Ok,
                self,
            ).exec()
            return False

        font_family = self.combobox_family.currentText()
        if font_family.isspace():
            self.combobox_family.lineEdit().setFocus()
            self.combobox_family.lineEdit().selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Empty Font Family",
                "Font family should not be left empty.",
                QMessageBox.StandardButton.Ok,
                self,
            ).exec()
            return False
        if font_family not in QFontDatabase.families():
            self.combobox_family.lineEdit().setFocus()
            self.combobox_family.lineEdit().selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Font Family Not Found",
                f'Found no font family named "{font_family}". Please check and try again.',
                QMessageBox.StandardButton.Ok,
                self,
            ).exec()
            return False
        return True

    def apply_settings(self) -> None:
        # Font
        key = f"{self.name}/font-family"
        family = self.combobox_family.currentText()
        Ng_Settings.setValue(key, family)

        key = f"{self.name}/font-size"
        size = self.spinbox_point_size.value()
        Ng_Settings.setValue(key, size)

        key = f"{self.name}/font-italic"
        is_italic = self.checkbox_italic.isChecked()
        Ng_Settings.setValue(key, is_italic)

        key = f"{self.name}/font-bold"
        is_bold = self.checkbox_bold.isChecked()
        Ng_Settings.setValue(key, is_bold)

        Ng_QSS.set_value(
            self.main,
            {
                "*": {
                    "font-family": family,
                    "font-size": f"{size}pt",
                    "font-style": "italic" if is_italic else "normal",
                    "font-weight": "bold" if is_bold else "normal",
                }
            },
        )
